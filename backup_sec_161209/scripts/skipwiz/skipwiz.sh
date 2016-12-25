#! /bin/bash

echo "Wating adb device.."
adb wait-for-device

echo "Skip setup wizard"
adb shell setprop persist.sys.setupwizard FINISH
adb shell am force-stop com.sec.android.app.SecSetupWizard
