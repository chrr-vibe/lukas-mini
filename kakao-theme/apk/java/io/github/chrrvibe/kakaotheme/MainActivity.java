package io.github.chrrvibe.kakaotheme;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.view.Gravity;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.Toast;

/** 테마 앱을 열면: 실행화면 그림(제복 레오 + 루카스) 아래 '테마 적용하기' 버튼 → 카카오톡 테마 설정. */
public final class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle saved) {
        super.onCreate(saved);
        float d = getResources().getDisplayMetrics().density;
        getWindow().setStatusBarColor(Color.parseColor("#3d3a7a"));
        getWindow().setNavigationBarColor(Color.parseColor("#2f2d63"));

        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(Color.parseColor("#3d3a7a"));
        ImageView art = new ImageView(this);
        art.setImageResource(R.drawable.theme_splash_image);
        art.setScaleType(ImageView.ScaleType.CENTER_CROP);
        root.addView(art, new FrameLayout.LayoutParams(-1, -1));

        Button apply = new Button(this);
        apply.setText("테마 적용하기");
        apply.setTextSize(17);
        apply.setTextColor(Color.parseColor("#2b2050"));
        apply.setAllCaps(false);
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(Color.WHITE);
        bg.setCornerRadius(12 * d);
        bg.setStroke(Math.round(1 * d), Color.parseColor("#e6dcff"));
        apply.setBackground(bg);
        FrameLayout.LayoutParams lp = new FrameLayout.LayoutParams(-1, Math.round(56 * d), Gravity.BOTTOM);
        lp.setMargins(Math.round(20 * d), 0, Math.round(20 * d), Math.round(28 * d));
        root.addView(apply, lp);
        apply.setOnClickListener(v -> {
            try {
                startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("kakaotalk://settings/theme/" + getPackageName()))
                        .setPackage("com.kakao.talk"));
                finish();
            } catch (ActivityNotFoundException e) {
                Toast.makeText(this, "카카오톡 → 설정 → 화면 → 테마 에서 골라 주세요.", Toast.LENGTH_LONG).show();
            }
        });
        setContentView(root);
    }
}
