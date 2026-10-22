package io.github.chrpvibe.lucasgotchimini;

import android.content.Context;
import android.content.SharedPreferences;
import android.net.Uri;
import android.util.Base64;

import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;

/** 위젯 그림 파일 + 설정(manifest) 저장소. 그림은 앱 화면(index.html)이 만들어서 넘겨 줌. */
final class Store {
    private Store() {}

    static SharedPreferences prefs(Context c) {
        return c.getSharedPreferences("lg", Context.MODE_PRIVATE);
    }

    static File dir(Context c) {
        File d = new File(c.getFilesDir(), "widget");
        if (!d.exists()) d.mkdirs();
        return d;
    }

    /** 파일 이름은 영어 소문자·숫자·밑줄 + .img 만 (다른 경로로 새지 않게) */
    static boolean validName(String n) {
        return n != null && n.matches("[a-z0-9_]{1,60}\\.img");
    }

    static void putFile(Context c, String name, String base64) throws IOException {
        if (!validName(name) || base64 == null) return;
        byte[] data = Base64.decode(base64, Base64.DEFAULT);
        File tmp = new File(dir(c), name + ".tmp");
        try (FileOutputStream out = new FileOutputStream(tmp)) {
            out.write(data);
        }
        File dst = new File(dir(c), name);
        if (!tmp.renameTo(dst)) {
            dst.delete();
            tmp.renameTo(dst);
        }
    }

    static JSONObject manifest(Context c) {
        String s = prefs(c).getString("manifest", null);
        if (s == null) return null;
        try {
            JSONObject o = new JSONObject(s);
            return o.has("ver") ? o : null;
        } catch (Exception e) {
            return null;
        }
    }

    static String manifestRaw(Context c) {
        String s = prefs(c).getString("manifest", null);
        return s == null ? "" : s;
    }

    static void setManifest(Context c, String json) {
        prefs(c).edit().putString("manifest", json).apply();
    }

    /** ?v= 는 그림이 바뀌었을 때 홈 화면이 옛 그림을 계속 쓰지 않게 붙이는 번호 */
    static Uri uri(Context c, String name, long ver) {
        return Uri.parse("content://" + c.getPackageName() + ".files/" + name + "?v=" + ver);
    }
}
