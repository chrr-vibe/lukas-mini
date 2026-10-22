package io.github.chrpvibe.lucasgotchimini;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.view.View;
import android.widget.RemoteViews;

import org.json.JSONObject;

/** 홈 화면 다마고치 위젯. 왼쪽 쓰다듬기 · 가운데 재우기 · 오른쪽 밥 먹기, 화면을 누르면 앱 열기. */
public class LgWidget extends AppWidgetProvider {
    static final String ACT_PET = "io.github.chrpvibe.lucasgotchimini.PET";
    static final String ACT_SLEEP = "io.github.chrpvibe.lucasgotchimini.SLEEP";
    static final String ACT_EAT = "io.github.chrpvibe.lucasgotchimini.EAT";
    static final String ACT_REFRESH = "io.github.chrpvibe.lucasgotchimini.REFRESH";

    // 위젯 그림 판 비율 (index.html 의 WBOX, layout/widget.xml 과 같아야 함)
    static final float BOX_W = 398f, BOX_H = 518f;

    @Override
    public void onUpdate(Context ctx, AppWidgetManager mgr, int[] ids) {
        updateAll(ctx);
    }

    @Override
    public void onAppWidgetOptionsChanged(Context ctx, AppWidgetManager mgr, int id, Bundle opts) {
        updateAll(ctx);
    }

    @Override
    public void onDisabled(Context ctx) {
        AlarmManager am = (AlarmManager) ctx.getSystemService(Context.ALARM_SERVICE);
        if (am != null) am.cancel(broadcast(ctx, ACT_REFRESH, 9));
    }

    @Override
    public void onReceive(Context ctx, Intent intent) {
        super.onReceive(ctx, intent);
        String a = intent.getAction();
        if (a == null) return;
        String what = ACT_PET.equals(a) ? "pet" : ACT_SLEEP.equals(a) ? "sleep" : ACT_EAT.equals(a) ? "eat" : null;
        if (what != null) {
            final Context app = ctx.getApplicationContext();
            final PendingResult pr = goAsync();
            long now = System.currentTimeMillis();
            GameState g = GameState.load(app);
            g.press(what, now);
            g.save(app);
            buzz(app);
            updateAll(app);
            if (g.action != null) {   // 쓰다듬기·밥 먹기가 끝나면 원래 모습으로
                long wait = Math.max(0, g.actionUntil - now) + 120;
                new Handler(Looper.getMainLooper()).postDelayed(() -> {
                    try {
                        updateAll(app);
                    } finally {
                        pr.finish();
                    }
                }, wait);
            } else {
                pr.finish();
            }
        } else if (ACT_REFRESH.equals(a)) {
            updateAll(ctx);
        }
    }

    /** 모든 위젯 다시 그리기 + 다음에 다시 그릴 시각 예약 */
    static synchronized void updateAll(Context ctx) {
        AppWidgetManager mgr = AppWidgetManager.getInstance(ctx);
        int[] ids = mgr.getAppWidgetIds(new ComponentName(ctx, LgWidget.class));
        if (ids == null || ids.length == 0) return;
        long now = System.currentTimeMillis();
        GameState g = GameState.load(ctx);
        g.evaluate(now);
        g.save(ctx);
        JSONObject man = Store.manifest(ctx);
        for (int id : ids) {
            try {
                mgr.updateAppWidget(id, build(ctx, mgr, id, g, man, now));
            } catch (Exception ignored) {
            }
        }
        scheduleNext(ctx, g, now);
    }

    static RemoteViews build(Context ctx, AppWidgetManager mgr, int id, GameState g, JSONObject man, long now) {
        String pkg = ctx.getPackageName();
        RemoteViews rv = new RemoteViews(pkg, R.layout.widget);

        // 다마고치 비율 맞추기 (남는 쪽에 여백)
        Bundle op = mgr.getAppWidgetOptions(id);
        int wdp = op == null ? 0 : op.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_WIDTH);
        int hdp = op == null ? 0 : op.getInt(AppWidgetManager.OPTION_APPWIDGET_MAX_HEIGHT);
        if (wdp > 0 && hdp > 0) {
            float d = ctx.getResources().getDisplayMetrics().density;
            float w = wdp * d, h = hdp * d, ar = BOX_W / BOX_H;
            int px = 0, py = 0;
            if (w / h > ar) px = (int) ((w - h * ar) / 2f);
            else py = (int) ((h - w / ar) / 2f);
            rv.setViewPadding(R.id.box, px, py, px, py);
        }

        if (man == null) {   // 앱을 아직 안 열어서 그림이 없음
            rv.setImageViewResource(R.id.shell, R.drawable.widget_preview);
            rv.setViewVisibility(R.id.flip, View.GONE);
            rv.setViewVisibility(R.id.bg, View.GONE);
            rv.setViewVisibility(R.id.hint, View.VISIBLE);
        } else {
            long ver = man.optLong("ver", 1);
            rv.setViewVisibility(R.id.hint, View.GONE);
            rv.setImageViewUri(R.id.shell, Store.uri(ctx, "shell.img", ver));

            String mode = g.mode(now);
            JSONObject modes = man.optJSONObject("modes");
            JSONObject mm = modes == null ? null : modes.optJSONObject(mode);
            int n = mm == null ? 1 : Math.max(1, mm.optInt("n", 1));
            int ms = mm == null ? 300 : Math.max(60, mm.optInt("ms", 300));
            String key = g.variantKey(now);
            rv.removeAllViews(R.id.flip);
            for (int i = 0; i < n; i++) {
                RemoteViews f = new RemoteViews(pkg, R.layout.widget_frame);
                f.setImageViewUri(R.id.frame, Store.uri(ctx, "lcd_" + key + "_" + i + ".img", ver));
                rv.addView(R.id.flip, f);
            }
            rv.setInt(R.id.flip, "setFlipInterval", ms);
            rv.setDisplayedChild(R.id.flip, 0);
            rv.setViewVisibility(R.id.flip, View.VISIBLE);

            if (man.optBoolean("bg", false)) {
                rv.setImageViewUri(R.id.bg, Store.uri(ctx, "bg.img", ver));
                rv.setViewVisibility(R.id.bg, View.VISIBLE);
            } else {
                rv.setViewVisibility(R.id.bg, View.GONE);
            }
        }

        rv.setOnClickPendingIntent(R.id.btnA, broadcast(ctx, ACT_PET, 1));
        rv.setOnClickPendingIntent(R.id.btnB, broadcast(ctx, ACT_SLEEP, 2));
        rv.setOnClickPendingIntent(R.id.btnC, broadcast(ctx, ACT_EAT, 3));
        Intent open = new Intent(ctx, MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        rv.setOnClickPendingIntent(R.id.screen, PendingIntent.getActivity(ctx, 0, open,
                PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT));
        return rv;
    }

    static PendingIntent broadcast(Context ctx, String action, int req) {
        Intent i = new Intent(ctx, LgWidget.class).setAction(action);
        return PendingIntent.getBroadcast(ctx, req, i, PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
    }

    /** 낮↔밤, 눈물(10분), 땀(1시간), 배고픔(3시간), 행동 끝 중 가장 빠른 때에 다시 그림 */
    static void scheduleNext(Context ctx, GameState g, long now) {
        long next = now + GameState.msToDayNightSwitch(now) + 500;
        if (!g.sleeping) {
            if (!g.cry) next = Math.min(next, g.lastPet + GameState.CRY_AFTER + 1000);
            if (!g.sick) next = Math.min(next, g.lastSleep + GameState.SICK_AFTER + 1000);
            if (!g.hungry) next = Math.min(next, g.lastEat + GameState.HUNGRY_AFTER + 1000);
        }
        if (g.action != null) next = Math.min(next, g.actionUntil + 150);
        next = Math.max(next, now + 1000);
        AlarmManager am = (AlarmManager) ctx.getSystemService(Context.ALARM_SERVICE);
        if (am != null) am.set(AlarmManager.RTC, next, broadcast(ctx, ACT_REFRESH, 9));
    }

    static void buzz(Context ctx) {
        try {
            Vibrator v = (Vibrator) ctx.getSystemService(Context.VIBRATOR_SERVICE);
            if (v == null || !v.hasVibrator()) return;
            if (Build.VERSION.SDK_INT >= 29) v.vibrate(VibrationEffect.createPredefined(VibrationEffect.EFFECT_TICK));
            else v.vibrate(VibrationEffect.createOneShot(15, VibrationEffect.DEFAULT_AMPLITUDE));
        } catch (Exception ignored) {
        }
    }
}
