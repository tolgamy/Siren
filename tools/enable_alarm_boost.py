from pathlib import Path

root=Path("project/kullanici/src/main")
sound=root/"java/com/ornek/sirenkullanici/SirenSound.java"
activity=root/"java/com/ornek/sirenkullanici/MainActivity.java"
manifest=root/"AndroidManifest.xml"

def sub(s,a,b):
    if s.count(a)!=1: raise RuntimeError("patch target not unique: "+a[:50])
    return s.replace(a,b)

s=sound.read_text()
s=sub(s,"import android.media.AudioTrack;","import android.media.AudioTrack;\nimport android.media.AudioManager;\nimport android.util.Log;")
s=sub(s,"    private static Thread thread;","""    private static Thread thread;
    private static AudioManager boostedManager;
    private static int previousLevel=-1;
    private static int boostedLevel=-1;""")
s=sub(s,"        thread = null;\n    }\n    private static void runAudio",'''        thread = null;
        restoreAlarmVolume();
    }
    private static synchronized void raiseVolume(Context ctx, int run) {
        if (generation.get()!=run || !Wire.prefs(ctx).getBoolean("boost_alarm",false)) return;
        try {
            AudioManager am=(AudioManager)ctx.getSystemService(Context.AUDIO_SERVICE);
            if (am==null || am.isVolumeFixed()) return;
            int old=am.getStreamVolume(AudioManager.STREAM_ALARM);
            int max=am.getStreamMaxVolume(AudioManager.STREAM_ALARM);
            int target=Math.max(1,(int)Math.ceil(max*0.80));
            if (old>=target) return;
            am.setStreamVolume(AudioManager.STREAM_ALARM,target,0);
            int actual=am.getStreamVolume(AudioManager.STREAM_ALARM);
            if (actual>old) { boostedManager=am; previousLevel=old; boostedLevel=actual; }
        } catch (Exception e) {
            Log.w("SirenKullanici","Could not raise alarm volume",e);
            Wire.prefs(ctx).edit().putString("last_audio_error","Alarm sesi yukseltilemedi. Rahatsiz Etmeyin ayarlarini kontrol et.").apply();
        }
    }
    private static synchronized void restoreAlarmVolume() {
        if (boostedManager!=null && previousLevel>=0) {
            try {
                if (boostedManager.getStreamVolume(AudioManager.STREAM_ALARM)==boostedLevel)
                    boostedManager.setStreamVolume(AudioManager.STREAM_ALARM,previousLevel,0);
            } catch (Exception e) { Log.w("SirenKullanici","Could not restore alarm volume",e); }
        }
        boostedManager=null; previousLevel=-1; boostedLevel=-1;
    }
    private static synchronized void restoreIfCurrent(int run) {
        if (generation.get()==run) restoreAlarmVolume();
    }
    private static void runAudio''')
s=sub(s,"            int rate = 22050;","            raiseVolume(ctx,myGeneration);\n            int rate = 22050;")
s=sub(s,"            if (wl != null && wl.isHeld()) wl.release();","            if (wl != null && wl.isHeld()) wl.release();\n            restoreIfCurrent(myGeneration);")
sound.write_text(s)

a=activity.read_text()
a=sub(a,"import android.app.NotificationManager;","import android.app.NotificationManager;\nimport android.media.AudioManager;")
a=sub(a,'''        button(area, "BU TELEFONDA SİRENİ TEST ET", () -> {
            SirenSound.start(this); status.setText("30 saniyelik test başladı. Alarm ses seviyesi sıfır olmamalı.");
        });''','''        addText(area, "İsteğe bağlı: Siren başlarken alarm sesini %80'e yükseltip bitince eski seviyeye döndürür. Rahatsız Etmeyin alarmları engelliyorsa işe yaramayabilir.", 14);
        button(area, "SİREN SESİNİ OTOMATİK YÜKSELT / KAPAT", () -> {
            boolean enabled = !Wire.prefs(this).getBoolean("boost_alarm",false);
            Wire.prefs(this).edit().putBoolean("boost_alarm",enabled).apply();
            status.setText(enabled ? "Alarm sesini otomatik yükseltme: AÇIK" : "Alarm sesini otomatik yükseltme: KAPALI");
        });
        button(area, "BU TELEFONDA SİRENİ TEST ET", () -> {
            SirenSound.start(this);
            AudioManager am = (AudioManager)getSystemService(AUDIO_SERVICE);
            status.setText("30 saniyelik test başladı. Alarm sesi "
                +(am==null ? "bilinmiyor" : am.getStreamVolume(AudioManager.STREAM_ALARM))
                +". Otomatik yükseltme: "+(Wire.prefs(this).getBoolean("boost_alarm",false)?"AÇIK":"KAPALI"));
        });''')
activity.write_text(a)

m=manifest.read_text()
m=sub(m,'    <uses-permission android:name="android.permission.WAKE_LOCK"/>','    <uses-permission android:name="android.permission.WAKE_LOCK"/>\n    <uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS"/>')
manifest.write_text(m)

for file in [Path("project/ana/build.gradle"),Path("project/kullanici/build.gradle")]:
    g=file.read_text()
    g=sub(g,"versionCode 3","versionCode 4")
    g=sub(g,"versionName '2.1'","versionName '2.2'")
    file.write_text(g)
print("Opt-in alarm volume boost applied")
