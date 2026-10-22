package io.github.chrpvibe.lucasgotchimini;

import android.app.Activity;
import android.appwidget.AppWidgetManager;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import org.json.JSONObject;

/** GitHub Pages 의 LUCASGOTCHI mini 를 띄우는 화면 + 위젯과 상태를 주고받는 다리(LGAndroid) */
public class MainActivity extends Activity {
    private static final int REQ_FILE = 7;
    private WebView web;
    private ValueCallback<Uri[]> fileCb;
    private String home;

    @Override
    protected void onCreate(Bundle saved) {
        super.onCreate(saved);
        home = getString(R.string.web_url);
        web = new WebView(this);
        web.setBackgroundColor(Color.parseColor("#fde9f3"));
        setContentView(web);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setAllowFileAccess(false);
        s.setUserAgentString(s.getUserAgentString() + " LGMiniApp");

        web.addJavascriptInterface(new Bridge(getApplicationContext()), "LGAndroid");
        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
                Uri u = req.getUrl();
                if (sameSite(u)) return false;
                try {   // 바깥 링크(앱 받기 등)는 브라우저로
                    startActivity(new Intent(Intent.ACTION_VIEW, u));
                } catch (Exception ignored) {
                }
                return true;
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest req, WebResourceError err) {
                if (req.isForMainFrame()) view.loadDataWithBaseURL(null, offlinePage(), "text/html", "utf-8", null);
            }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> cb, FileChooserParams params) {
                if (fileCb != null) fileCb.onReceiveValue(null);
                fileCb = cb;
                try {   // '+ add background' 사진 고르기
                    startActivityForResult(params.createIntent(), REQ_FILE);
                } catch (Exception e) {
                    fileCb = null;
                    return false;
                }
                return true;
            }
        });

        if (saved != null) web.restoreState(saved);
        else web.loadUrl(home);
    }

    private boolean sameSite(Uri u) {
        Uri h = Uri.parse(home);
        return u != null && h.getHost() != null && h.getHost().equalsIgnoreCase(u.getHost())
                && u.getPath() != null && u.getPath().startsWith(h.getPath() == null ? "/" : h.getPath());
    }

    private String offlinePage() {
        return "<html><head><meta name='viewport' content='width=device-width,initial-scale=1'></head>"
                + "<body style='margin:0;font-family:sans-serif;background:#fde9f3;color:#3b2a46;text-align:center;padding-top:45%'>"
                + "인터넷에 연결되지 않았어.<br>처음 한 번은 인터넷이 필요해.<br><br>"
                + "<button style='font-size:16px;padding:8px 18px;border:3px solid #3b2a46;border-radius:99px;background:#fff' "
                + "onclick=\"location.href='" + home + "'\">다시 시도</button></body></html>";
    }

    @Override
    protected void onActivityResult(int req, int res, Intent data) {
        super.onActivityResult(req, res, data);
        if (req == REQ_FILE && fileCb != null) {
            fileCb.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(res, data));
            fileCb = null;
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        web.onResume();
        web.evaluateJavascript("window.lgResume&&lgResume()", null);
    }

    @Override
    protected void onPause() {
        web.evaluateJavascript("window.lgPause&&lgPause()", null);
        web.onPause();
        super.onPause();
    }

    @Override
    protected void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out);
        web.saveState(out);
    }

    @Override
    public void onBackPressed() {
        if (web.canGoBack()) web.goBack();
        else super.onBackPressed();
    }

    /** index.html 이 window.LGAndroid 로 부르는 함수들 */
    static class Bridge {
        private final Context ctx;

        Bridge(Context ctx) {
            this.ctx = ctx;
        }

        @JavascriptInterface
        public String getState() {
            String s = Store.prefs(ctx).getString("state", null);
            if (s == null) return "";
            GameState g = GameState.load(ctx);
            g.evaluate(System.currentTimeMillis());
            return g.json();
        }

        /** 앱에서 바뀐 상태. 위젯에서 더 나중에 누른 게 있으면(stamp가 더 큼) 무시 */
        @JavascriptInterface
        public void setState(String json) {
            try {
                JSONObject o = new JSONObject(json);
                long now = System.currentTimeMillis();
                GameState g = GameState.load(ctx);
                if (o.optLong("stamp", 0) < g.stamp) return;
                boolean first = Store.prefs(ctx).getString("state", null) == null;
                g.evaluate(now);
                String before = g.variantKey(now);
                g.read(o);
                g.evaluate(now);
                g.save(ctx);
                if (first || !before.equals(g.variantKey(now))) LgWidget.updateAll(ctx);
            } catch (Exception ignored) {
            }
        }

        @JavascriptInterface
        public String getManifest() {
            return Store.manifestRaw(ctx);
        }

        @JavascriptInterface
        public void putFile(String name, String base64) {
            try {
                Store.putFile(ctx, name, base64);
            } catch (Exception ignored) {
            }
        }

        @JavascriptInterface
        public void commit(String manifest) {
            Store.setManifest(ctx, manifest);
            LgWidget.updateAll(ctx);
        }

        /** '+ 홈 화면에 추가' 버튼 */
        @JavascriptInterface
        public boolean pinWidget() {
            try {
                AppWidgetManager m = AppWidgetManager.getInstance(ctx);
                if (!m.isRequestPinAppWidgetSupported()) return false;
                return m.requestPinAppWidget(new ComponentName(ctx, LgWidget.class), null, null);
            } catch (Exception e) {
                return false;
            }
        }
    }
}
