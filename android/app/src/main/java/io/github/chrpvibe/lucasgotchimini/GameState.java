package io.github.chrpvibe.lucasgotchimini;

import android.content.Context;

import org.json.JSONObject;

import java.util.Calendar;

/**
 * 루카스 상태 (앱과 위젯이 같이 씀). 규칙은 index.html 의 메인 루프와 같음:
 *  - 자는 동안: 건강·멘탈 시간이 계속 채워짐
 *  - 안 자고 1시간 지나면 아픔(땀), 안 쓰다듬고 10분 지나면 울음(눈물)
 *  - 쓰다듬기 1.8초 (울음 해제) / 밥 먹기 5초 / 재우기는 다시 누를 때까지 (아픔 해제)
 *  stamp: 마지막으로 누른 시각. 앱과 위젯 중 더 최근에 누른 쪽 상태를 씀.
 */
final class GameState {
    static final long SICK_AFTER = 60 * 60 * 1000L;
    static final long CRY_AFTER = 10 * 60 * 1000L;
    static final long PET_MS = 1800L;
    static final long EAT_MS = 5000L;

    long stamp, lastPet, lastSleep, lastEat, actionUntil;
    boolean sick, cry, sleeping;
    String action;            // "pet" / "eat" / null
    JSONObject raw = new JSONObject();   // 옷·테마·배경 등 앱이 넘긴 나머지 값 (복구용)

    static GameState load(Context c) {
        GameState g = new GameState();
        long now = System.currentTimeMillis();
        g.lastPet = g.lastSleep = g.lastEat = now;
        String s = Store.prefs(c).getString("state", null);
        if (s != null) {
            try {
                g.read(new JSONObject(s));
            } catch (Exception ignored) {
            }
        }
        return g;
    }

    void read(JSONObject o) {
        raw = o;
        stamp = o.optLong("stamp", stamp);
        lastPet = o.optLong("lastPet", lastPet);
        lastSleep = o.optLong("lastSleep", lastSleep);
        lastEat = o.optLong("lastEat", lastEat);
        sick = o.optBoolean("sick", sick);
        cry = o.optBoolean("cry", cry);
        sleeping = o.optBoolean("sleeping", sleeping);
        Object a = o.opt("action");
        action = ("pet".equals(a) || "eat".equals(a)) ? (String) a : null;
        actionUntil = action == null ? 0 : o.optLong("actionUntil", 0);
    }

    String json() {
        try {
            JSONObject o = new JSONObject(raw.toString());
            o.put("stamp", stamp);
            o.put("lastPet", lastPet);
            o.put("lastSleep", lastSleep);
            o.put("lastEat", lastEat);
            o.put("sick", sick);
            o.put("cry", cry);
            o.put("sleeping", sleeping);
            o.put("action", action == null ? JSONObject.NULL : action);
            o.put("actionUntil", actionUntil);
            return o.toString();
        } catch (Exception e) {
            return "{}";
        }
    }

    void save(Context c) {
        Store.prefs(c).edit().putString("state", json()).apply();
    }

    /** 시간이 흐른 만큼 상태를 맞춤 (앱 메인 루프와 같은 규칙) */
    void evaluate(long now) {
        if ("eat".equals(action)) lastEat = Math.min(now, actionUntil);
        if (action != null && now >= actionUntil) {
            action = null;
            actionUntil = 0;
        }
        if (sleeping) {
            lastSleep = now;
            lastPet = now;
            sick = false;
        } else {
            if (!sick && now - lastSleep > SICK_AFTER) sick = true;
            if (!cry && now - lastPet > CRY_AFTER) cry = true;
        }
    }

    /** 위젯 버튼: pet(왼쪽) / sleep(가운데) / eat(오른쪽) */
    void press(String what, long now) {
        evaluate(now);
        boolean wasSleeping = sleeping;
        if (sleeping) {           // 자는 중에 쓰다듬기·밥 먹기 → 깨우고 바로 그 행동
            sleeping = false;
            lastSleep = now;
            lastPet = now;
        }
        switch (what) {
            case "pet":
                cry = false;
                lastPet = now;
                action = "pet";
                actionUntil = now + PET_MS;
                break;
            case "eat":
                action = "eat";
                actionUntil = now + EAT_MS;
                lastEat = now;
                break;
            case "sleep":
                action = null;
                actionUntil = 0;
                if (!wasSleeping) {   // 재우기 (이미 자고 있었으면 위에서 깨움)
                    sleeping = true;
                    sick = false;
                }
                break;
            default:
                return;
        }
        stamp = now;
    }

    String mode(long now) {
        if (sleeping) return "sleep";
        if (action != null && now < actionUntil) return action;
        return "idle";
    }

    /** 위젯 그림 이름 (index.html 의 wVariants 와 같은 규칙) */
    String variantKey(long now) {
        String m = mode(now);
        String n = isNight(now) ? "n" : "d";
        String s = sick ? "s" : "x";
        switch (m) {
            case "sleep":
                return "sleep_" + n;
            case "pet":
            case "eat":
                return m + "_" + n + "_" + s;
            default:
                return "idle_" + n + "_" + s + (cry ? "c" : "x");
        }
    }

    /** 게임 시계: 현실 1시간 = 게임 24시간. 게임 오후 7시 ~ 오전 6시가 밤 */
    static boolean isNight(long now) {
        double gm = msInHour(now) / 3600000.0 * 1440.0;
        int h = (int) (gm / 60);
        return h >= 19 || h < 6;
    }

    static long msInHour(long now) {
        Calendar c = Calendar.getInstance();
        c.setTimeInMillis(now);
        return (c.get(Calendar.MINUTE) * 60L + c.get(Calendar.SECOND)) * 1000L + c.get(Calendar.MILLISECOND);
    }

    /** 다음 낮↔밤 바뀌는 시각까지 남은 ms (게임 6시 = 현실 15분, 게임 19시 = 현실 47분 30초) */
    static long msToDayNightSwitch(long now) {
        long m = msInHour(now);
        final long DAY = 15 * 60 * 1000L, NIGHT = 47 * 60 * 1000L + 30 * 1000L, HOUR = 60 * 60 * 1000L;
        if (m < DAY) return DAY - m;
        if (m < NIGHT) return NIGHT - m;
        return HOUR - m + DAY;
    }
}
