from pathlib import Path
import math, struct, wave
root=Path("project")
src=root/"kullanici/src/main"
sound=src/"java/com/ornek/sirenkullanici/SirenSound.java"
s=sound.read_text(encoding="utf-8")
def once(s,a,b):
    if s.count(a)!=1: raise RuntimeError("Patch mismatch: "+a[:80])
    return s.replace(a,b)
s=once(s,"import android.media.AudioTrack;","import android.media.AudioTrack;\nimport android.media.MediaPlayer;")
s=once(s,"            boostAlarmVolume(ctx, myGeneration);\n            int rate = 22050;",'''
            boostAlarmVolume(ctx, myGeneration);
            if (Wire.prefs(ctx).getBoolean("compatible_player", true)) {
                AudioAttributes attributes = new AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_ALARM)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION).build();
                MediaPlayer mp = MediaPlayer.create(ctx, R.raw.siren_alarm, attributes, 0);
                if (mp != null) {
                    try {
                        mp.setVolume(1.0f, 1.0f);
                        mp.setLooping(true);
                        if (generation.get() == myGeneration) {
                            mp.start();
                            Wire.prefs(ctx).edit().putString("last_audio_player","UYUMLU (MediaPlayer)").apply();
                            long begin = SystemClock.elapsedRealtime();
                            while (generation.get() == myGeneration && !Thread.currentThread().isInterrupted()
                                    && SystemClock.elapsedRealtime()-begin < 30000) Thread.sleep(100);
                        }
                        return;
                    } finally {
                        try { if (mp.isPlaying()) mp.stop(); } catch (Exception ignored) {}
                        mp.release();
                    }
                }
                Wire.prefs(ctx).edit().putString("last_audio_error","Uyumlu ses oynatici acilamadi").apply();
            }
            int rate = 22050;''')
s=once(s,"            track.play();","            track.play();\n            Wire.prefs(ctx).edit().putString(\"last_audio_player\",\"KLASIK (AudioTrack)\").apply();")
s=once(s,"        } catch (Exception e) { android.util.Log.e(\"SirenKullanici\", \"Ses hatası\", e); }",'''        } catch (Exception e) {
            android.util.Log.e("SirenKullanici", "Ses hatası", e);
            Wire.prefs(ctx).edit().putString("last_audio_error",
                    e.getClass().getSimpleName()+": "+e.getMessage()).apply();
        }''')
sound.write_text(s,encoding="utf-8")

raw=src/"res/raw"
raw.mkdir(parents=True,exist_ok=True)
with wave.open(str(raw/"siren_alarm.wav"),"wb") as audio:
    audio.setnchannels(1);audio.setsampwidth(2);audio.setframerate(22050)
    data=[]; phase=0.0
    for n in range(22050*3):
        t=n/22050.0
        triangle=(t/0.8)%2
        hz=620+530*(triangle if triangle<1 else 2-triangle)
        phase+=2*math.pi*hz/22050
        envelope=min(1.0,12*t,12*(3-t))
        data.append(int(23000*max(0,envelope)*math.sin(phase)))
    audio.writeframes(struct.pack("<%dh"%len(data),*data))

activity=src/"java/com/ornek/sirenkullanici/MainActivity.java"
s=activity.read_text(encoding="utf-8")
s=once(s,"import android.media.AudioManager;","import android.media.AudioManager;\nimport android.provider.Settings;")
s=once(s,'''        button(area, "BU TELEFONDA SİRENİ TEST ET", () -> {''','''
        addText(area,"Sessiz modda ses cikmazsa UYUMLU ses yontemini dene. Ses seviyesi ve Rahatsiz Etmeyin durumunu kontrol et.",14);
        button(area,"UYUMLU / KLASİK SES YÖNTEMİNİ DEĞİŞTİR",() -> {
            boolean next=!Wire.prefs(this).getBoolean("compatible_player",true);
            Wire.prefs(this).edit().putBoolean("compatible_player",next).apply();
            status.setText(next ? "Ses yöntemi: UYUMLU" : "Ses yöntemi: KLASİK");
        });
        button(area,"SES DURUMUNU KONTROL ET",() -> {
            AudioManager am=(AudioManager)getSystemService(AUDIO_SERVICE);
            NotificationManager nm=getSystemService(NotificationManager.class);
            StringBuilder info=new StringBuilder("SES KONTROLÜ\\n");
            if(am!=null) {
                info.append("Alarm sesi: ").append(am.getStreamVolume(AudioManager.STREAM_ALARM))
                    .append("/").append(am.getStreamMaxVolume(AudioManager.STREAM_ALARM)).append("\\n");
                info.append("Telefon modu: ").append(am.getRingerMode()==AudioManager.RINGER_MODE_SILENT
                    ? "SESSİZ" : am.getRingerMode()==AudioManager.RINGER_MODE_VIBRATE
                    ? "TİTREŞİM" : "NORMAL").append("\\n");
            }
            if(nm!=null) info.append("Rahatsız Etmeyin kodu: ")
                .append(nm.getCurrentInterruptionFilter()).append("\\n")
                .append("(1 normal, 2 öncelikli, 3 tümü engelli, 4 sadece alarm)\\n");
            info.append("Yöntem: ").append(Wire.prefs(this).getBoolean("compatible_player",true)
                ? "UYUMLU":"KLASİK").append("\\n");
            info.append("Son çalma: ").append(Wire.prefs(this).getString("last_audio_player","YOK"))
                .append("\\nHata: ").append(Wire.prefs(this).getString("last_audio_error","YOK"));
            status.setText(info.toString());
        });
        button(area,"TELEFON SES AYARLARINI AÇ",() -> {
            try {startActivity(new Intent(Settings.ACTION_SOUND_SETTINGS));}
            catch(Exception e) {status.setText("Ayar açılamadı: "+e.getMessage());}
        });
        button(area, "BU TELEFONDA SİRENİ TEST ET", () -> {''')
activity.write_text(s,encoding="utf-8")
for module in ["ana","kullanici"]:
    f=root/module/"build.gradle"
    s=f.read_text(encoding="utf-8")
    s=once(s,"versionCode 4","versionCode 5")
    s=once(s,"versionName '2.2'","versionName '2.3'")
    s=once(s,"    compileOptions {",'''    signingConfigs {
        if (System.getenv('SIREN_KEYSTORE_PATH')) {
            persistent {
                storeFile file(System.getenv('SIREN_KEYSTORE_PATH'))
                storePassword System.getenv('SIREN_KEYSTORE_PASSWORD')
                keyAlias System.getenv('SIREN_KEY_ALIAS')
                keyPassword System.getenv('SIREN_KEY_PASSWORD')
            }
        }
    }
    buildTypes {
        debug {
            if (System.getenv('SIREN_KEYSTORE_PATH')) signingConfig signingConfigs.persistent
        }
    }
    compileOptions {''')
    f.write_text(s,encoding="utf-8")
print("Siren 2.3 ses deneme ve kalici imza altyapisi hazir")
