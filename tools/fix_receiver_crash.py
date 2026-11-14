from pathlib import Path

root = Path("project/kullanici/src/main/java/com/ornek/sirenkullanici")
service = root / "ListenerService.java"
text = service.read_text(encoding="utf-8")
old = """        Notification notice = makeNotification();
        if (Build.VERSION.SDK_INT >= 34) {
            startForeground(NOTICE_ID, notice, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE);
        } else { startForeground(NOTICE_ID, notice); }
"""
new = """        try {
            Notification notice = makeNotification();
            if (Build.VERSION.SDK_INT >= 34) {
                startForeground(NOTICE_ID, notice, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE);
            } else {
                startForeground(NOTICE_ID, notice);
            }
        } catch (RuntimeException | LinkageError e) {
            Log.e("SirenKullanici", "Dinleme bildirimi veya hizmet baslatilamadi", e);
            String description = e.getClass().getSimpleName() + ": " + String.valueOf(e.getMessage());
            Wire.prefs(this).edit().putBoolean("active", false).putString("last_error", description).apply();
            try { showLauncher(true); } catch (Exception ex) { Log.w("SirenKullanici", "Simge geri getirilemedi", ex); }
            stopSelf();
            return START_NOT_STICKY;
        }
"""
if text.count(old) != 1: raise RuntimeError("Beklenen hizmet kaynak kodu bulunamadi")
service.write_text(text.replace(old, new), encoding="utf-8")

activity = root / "MainActivity.java"
text = activity.read_text(encoding="utf-8")
old = """        status = addText(area, "Durum: " + (Wire.prefs(this).getBoolean("active", false) ? "Dinleme seçili" : "Dinleme kapalı"), 16);
"""
new = """        String previousError = Wire.prefs(this).getString("last_error", "");
        status = addText(area, previousError.isEmpty()
            ? "Durum: " + (Wire.prefs(this).getBoolean("active", false) ? "Dinleme seçili" : "Dinleme kapalı")
            : "Dinleme hizmeti hatası: " + previousError, 16);
"""
if text.count(old) != 1: raise RuntimeError("Beklenen durum satiri bulunamadi")
text = text.replace(old, new)
old = """    private void startListening() {
        askNotifications();
        Wire.prefs(this).edit().putBoolean("active", true).apply();
"""
new = """    private void startListening() {
        askNotifications();
        NotificationManager manager = getSystemService(NotificationManager.class);
        if (manager == null || !manager.areNotificationsEnabled()) {
            status.setText("Dinleme açılmadı. Önce bu uygulamanın bildirim iznini ver, sonra tekrar DİNLEMEYİ AÇ'a bas.");
            return;
        }
        Wire.prefs(this).edit().remove("last_error").putBoolean("active", true).apply();
"""
if text.count(old) != 1: raise RuntimeError("Beklenen dinleme baslangici bulunamadi")
text = text.replace(old, new)
old = """    private void stopListening() {
"""
new = """    @Override protected void onResume() {
        super.onResume();
        if (status != null) {
            String error = Wire.prefs(this).getString("last_error", "");
            if (!error.isEmpty()) status.setText("Dinleme hizmeti hatası: " + error);
        }
    }
    private void stopListening() {
"""
if text.count(old) != 1: raise RuntimeError("Beklenen durdurma metodu bulunamadi")
activity.write_text(text.replace(old, new), encoding="utf-8")

for gradle_file in [Path("project/ana/build.gradle"), Path("project/kullanici/build.gradle")]:
    gradle = gradle_file.read_text(encoding="utf-8")
    if "versionCode 2" not in gradle: raise RuntimeError("Beklenmeyen surum: " + str(gradle_file))
    gradle = gradle.replace("versionCode 2", "versionCode 3").replace("versionName '2.0'", "versionName '2.1'")
    gradle_file.write_text(gradle, encoding="utf-8")
print("Kullanici hizmet hata yakalama ve bildirim izni kontrolleri eklendi.")
