package com.v2ray.ang.ui

import android.os.Bundle
import android.widget.Toast
import com.v2ray.ang.R

/**
 * QR scanning is not available in this build.
 *
 * The upstream scanner pulls in io.github.g00fy2.quickie and the bundled
 * Barcode Scanning native library, both requiring Android API 21; this fork
 * targets API 19 (Android 4.4). Callers treat RESULT_CANCELED as "user
 * aborted", so their contract is preserved and the clipboard/subscription
 * import flows remain the way to add configurations.
 */
class ScannerActivity : BaseActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Toast.makeText(this, R.string.qr_scanner_unsupported, Toast.LENGTH_LONG).show()
        setResult(RESULT_CANCELED)
        finish()
    }

    companion object {
        const val SCAN_TEXT = "scan_text"
    }
}
