from pathlib import Path

root=Path("project")
src=root/"kullanici/src/main/java/com/ornek/sirenkullanici"
sound=src/"SirenSound.java"
ui=src/"MainActivity.java"

def one(s,old,new):
    count=s.count(old)
    if count!=1:
        raise RuntimeError("v2.4 expected 1 match, found "+str(count)+": "+old[:80])
    return s.replace(old,new)

s=sound.read_text(encoding="utf-8")
s=one(s,"    private static AudioManager boostedManager;","    private static AudioManager boostedManager;\n    private static int boostedStream=AudioManager.STREAM_MUSIC;")
s=one(s,'!Wire.prefs(ctx).getBoolean("boost_alarm", false)','!Wire.prefs(ctx).getBoolean("boost_alarm", true)')
s=one(s,'''            int old=am.getStreamVolume(AudioManager.STREAM_ALARM);
            int max=am.getStreamMaxVolume(AudioManager.STREAM_ALARM);''','''            int old=am.getStreamVolume(AudioManager.STREAM_MUSIC);
            int max=am.getStreamMaxVolume(AudioManager.STREAM_MUSIC);''')
s=one(s,'''            am.setStreamVolume(AudioManager.STREAM_ALARM,desired,0);
            int actual=am.getStreamVolume(AudioManager.STREAM_ALARM);
            if (actual>old) { boostedManager=am;previousAlarmLevel=old;boostedAlarmLevel=actual; }''','''            am.setStreamVolume(AudioManager.STREAM_MUSIC,desired,0);
            int actual=am.getStreamVolume(AudioManager.STREAM_MUSIC);
            if (actual>old) { boostedManager=am;boostedStream=AudioManager.STREAM_MUSIC;previousAlarmLevel=old;boostedAlarmLevel=actual; }''')
s=one(s,'"Alarm sesi sistem tarafindan yukseltilemedi"','"Medya sesi sistem tarafindan yukseltilemedi. Ses ayarlarini kontrol et."')
s=one(s,'''if (boostedManager.getStreamVolume(AudioManager.STREAM_ALARM)==boostedAlarmLevel)
                boostedManager.setStreamVolume(AudioManager.STREAM_ALARM,previousAlarmLevel,0);''','''if (boostedManager.getStreamVolume(boostedStream)==boostedAlarmLevel)
                boostedManager.setStreamVolume(boostedStream,previousAlarmLevel,0);''')
s=one(s,'''            .setUsage(AudioAttributes.USAGE_ALARM)
            .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION).build();''','''            .setUsage(AudioAttributes.USAGE_MEDIA)
            .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC).build();''')
sound.write_text(s,encoding="utf-8")

u=ui.read_text(encoding="utf-8")
u=one(u,"İsteğe bağlı: Alarm sesi kapalı olsa bile siren başlayınca alarm seviyesini %80'e yükseltir, bitince eski seviyeye döndürür. Rahatsız Etmeyin alarmları engelliyorsa yine ses çıkmayabilir.","Siren medya sesi üzerinden çalar. Sessiz modda otomatik medya sesini yükseltir, bitince eski seviyeye döndürür. Rahatsız Etmeyin medya seslerini engelliyorsa yine ses çıkmayabilir.")
u=one(u,"SİREN SIRASINDA ALARM SESİNİ YÜKSELT / KAPAT","SİREN SIRASINDA MEDYA SESİNİ YÜKSELT / KAPAT")
if u.count('Wire.prefs(this).getBoolean("boost_alarm", false)')!=2:
    raise RuntimeError("Unexpected count of volume settings")
u=u.replace('Wire.prefs(this).getBoolean("boost_alarm", false)','Wire.prefs(this).getBoolean("boost_alarm", true)')
u=one(u,"Otomatik alarm sesi: AÇIK. Siren sırasında geçici olarak %80'e yükseltilecek.","Otomatik medya sesi: AÇIK. Siren sırasında geçici olarak %85'e yükseltilecek.")
u=one(u,"Otomatik alarm sesi: KAPALI. Telefonun alarm ses seviyesi kullanılacak.","Otomatik medya sesi: KAPALI. Telefonun medya ses seviyesi kullanılacak.")
u=one(u,"SİREN SES KONTROLÜ\\n","SİREN SES KONTROLÜ (MEDYA SESİ)\\n")
u=one(u,"SirenSound.start(this);\n            AudioManager audio","SirenSound.start(this);\n            AudioManager audio")
ui.write_text(u,encoding="utf-8")

for module in ["ana","kullanici"]:
    build=root/module/"build.gradle"
    g=build.read_text(encoding="utf-8")
    g=one(g,"versionCode 5","versionCode 6")
    g=one(g,"versionName '2.3'","versionName '2.4'")
    build.write_text(g,encoding="utf-8")
print("Siren v2.4: media playback with automatic temporary media volume boost")
