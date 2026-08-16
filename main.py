@@
     def on_start(self):
         self.ads_error = None
         try:
             self.ads = KivMob(ADMOB_APP_ID)
             self.ads.new_banner(ADMOB_BANNER_ID, True)
             self.ads.request_banner()
             self.ads.show_banner()
 
-            self.ads.set_rewarded_ad_listener(RewardsHandler(self))
-            self.ads.load_rewarded_ad(ADMOB_REWARDED_ID)
+            self.ads.set_rewarded_ad_listener(RewardsHandler(self))
+            # Inisialisasi rewarded dengan fallback agar kompatibel dengan
+            # beberapa versi KivMob yang menggunakan API berbeda.
+            try:
+                if hasattr(self.ads, 'new_rewarded'):
+                    self.ads.new_rewarded(ADMOB_REWARDED_ID)
+                    # beberapa versi memerlukan request_rewarded()
+                    if hasattr(self.ads, 'request_rewarded'):
+                        self.ads.request_rewarded()
+                elif hasattr(self.ads, 'load_rewarded_ad'):
+                    self.ads.load_rewarded_ad(ADMOB_REWARDED_ID)
+                else:
+                    print("Wrapper KivMob tidak mendukung API rewarded yang dikenali.")
+            except Exception as e:
+                print("Gagal inisialisasi rewarded ad:", e)
         except Exception as e:
             print(f"Gagal Inisialisasi AdMob: {e}")
@@
         ad_shown = False
         if hasattr(self, 'ads'):
             try:
-                self.ads.show_rewarded_ad()
-                ad_shown = True
+                # Coba beberapa method umum untuk menampilkan rewarded
+                if hasattr(self.ads, 'show_rewarded'):
+                    self.ads.show_rewarded()
+                    ad_shown = True
+                elif hasattr(self.ads, 'show_rewarded_ad'):
+                    self.ads.show_rewarded_ad()
+                    ad_shown = True
+                elif hasattr(self.ads, 'show'):
+                    try:
+                        self.ads.show(ADMOB_REWARDED_ID)
+                        ad_shown = True
+                    except Exception:
+                        ad_shown = False
+                else:
+                    print("Tidak ada method show_rewarded pada KivMob yang terdeteksi.")
             except Exception as e:
                 print(f"AdMob error: {e}")
*** End Patch
