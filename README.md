# TRIPLE8SPIN - Build & AdMob Integration Notes

This branch `admob-integration` includes changes to integrate Google AdMob test ads (banner + rewarded) for Kivy using KivMob.

Quick setup

1. Install Buildozer and Android SDK/NDK according to https://github.com/kivy/buildozer and python-for-android docs.
2. Fetch the branch and switch to it:

   git fetch origin
   git checkout admob-integration

3. (Optional) If you want Telegram notifications, create a file `config.json` in the project root based on `config.sample.json` and fill in your bot token and chat id. This file is ignored by Git to avoid leaking tokens.

4. Build and deploy (example):

   buildozer android debug deploy run

Notes about ads

- The app uses Google test AdMob IDs by default. Keep those for testing:
  - App ID: ca-app-pub-3940256099942544~3347511713
  - Banner: ca-app-pub-3940256099942544/6300978111
  - Rewarded: ca-app-pub-3940256099942544/5224354917

- Use a real Android device with Google Play Services or an AVD image that includes Google Play. Many plain emulator images do not have Play Services and will not show ads.

Debugging

- To inspect logs related to ads and initialization, use adb logcat while running the app:

  adb logcat | grep -i "Ads\|AdMob\|com.google.android.gms.ads"

- Common issues:
  - "The Google Mobile Ads SDK was initialized incorrectly" → ensure the meta-data APPLICATION_ID is present in the Android manifest. The buildozer.spec in this branch already includes android.meta_data with the test App ID.
  - If KivMob wrapper API differs (method names), the code includes fallback checks to call either `new_rewarded`/`request_rewarded` or `load_rewarded_ad`, and to call `show_rewarded`, `show_rewarded_ad`, or `show(...)` when showing rewarded ads.

Security

- The repository previously contained Telegram bot credentials in main.py. This branch moves configuration to `config.json` (ignored) and provides `config.sample.json` as a template. Do not commit real tokens to the repository.

If you want, I can further:
- Remove the real token from commit history (requires force push and coordination).
- Add automated tests or CI to build the APK.

If you run into issues building or seeing ads, paste the adb logcat output and I will help debug.
