from pathlib import Path
root = Path("project")
src = root/"kullanici/src/main/java/com/ornek/sirenkullanici"
sound = src/"SirenSound.java"
ui = src/"MainActivity.java"
s = sound.read_text(encoding="utf-8")
# Both audio devices now play through the MUSIC stream instead of the ALARM stream.
assert s.count("AudioManager.STREAM_ALARM") >= 4, "Missing previous alarm stream mapping"
assert s.count("AudioAttributes.USAGE_ALARM") == 2, "Unexpected media player / audio track attributes"
assert s.count("AudioAttributes.CONTENT_TYPE_SONIFICATION") == 2, "Unexpected content type"
assert s.count('getBoolean("boost_alarm",false)') == 1, "Unexpected boost preference"
s = s.replace("AudioManager.STREAM_ALARM", "AudioManager.STREAM_MUSIC")
s = s.replace("AudioAttributes.USAGE_ALARM", "AudioAttributes.USAGE_MEDIA")
s = s.replace("AudioAttributes.CONTENT_TYPE_SONIFICATION", "AudioAttributes.CONTENT_TYPE_MUSIC")
s = s.replace('getBoolean("boost_alarm",false)', 'getBoolean("boost_alarm",true)')
s = s.replace("Alarm sesi yukseltilemedi", "Medya sesi yukseltilemedi")
sound.write_text(s, encoding="utf-8")
u = ui.read_text(encoding="utf-8")
assert u.count('getBoolean("boost_alarm",false)') == 2, "Unexpected UI boost preference"
assert 'SİREN SESİNİ OTOMATİK YÜKSELT / KAPAT' in u, "Expected volume control not found"
u = u.replace('getBoolean("boost_alarm",false)', 'getBoolean("boost_alarm",true)')
u = u.replace('SİREN SESİNİ OTOMATİK YÜKSELT / KAPAT', 'SİRENDE MEDYA SESİNİ YÜKSELT / KAPAT')
u = u.replace('alarm sesini', 'medya sesini').replace('alarm sesi', 'medya sesi')
u = u.replace('Alarm sesi', 'Medya sesi').replace('Otomatik alarm', 'Otomatik medya')
u = u.replace('AudioManager.STREAM_ALARM','AudioManager.STREAM_MUSIC')
u = u.replace('SES KONTROLÜ\\n','SES KONTROLÜ (MEDYA)\\n')
ui.write_text(u, encoding="utf-8")
for module in ("ana","kullanici"):
    path=root/module/"build.gradle"
    gradle=path.read_text(encoding="utf-8")
    assert gradle.count("versionCode 5")==1 and gradle.count("versionName '2.3'")==1, "Version unexpected"
    gradle=gradle.replace("versionCode 5","versionCode 6").replace("versionName '2.3'","versionName '2.4'")
    path.write_text(gradle,encoding="utf-8")
print("Siren 2.4: media volume playback and automatic boost enabled")
