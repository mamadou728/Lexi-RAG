"""
SSL Diagnostic Script for MongoDB Connection Issues
Run this to check your SSL/TLS configuration
"""
import sys
import ssl

print("=== Python & SSL Configuration ===\n")
print(f"Python Version: {sys.version}")
print(f"OpenSSL Version: {ssl.OPENSSL_VERSION}")
print(f"OpenSSL Version Info: {ssl.OPENSSL_VERSION_INFO}")
print(f"\nSupported TLS Versions:")
print(f"  - TLS 1.0: {hasattr(ssl, 'TLSVersion')}")
print(f"  - TLS 1.2 minimum: {ssl.TLSVersion.TLSv1_2 if hasattr(ssl, 'TLSVersion') else 'Unknown'}")

try:
    import certifi
    print(f"\nCertifi installed: ✅")
    print(f"Certificate bundle location: {certifi.where()}")
except ImportError:
    print(f"\nCertifi installed: ❌ (RUN: pip install certifi)")

try:
    import pymongo
    print(f"PyMongo version: {pymongo.__version__} ✅")
except ImportError:
    print(f"PyMongo: ❌")

try:
    import motor
    print(f"Motor version: {motor.version} ✅")
except ImportError:
    print(f"Motor: ❌")

print("\n=== Recommendations ===")
if ssl.OPENSSL_VERSION_INFO < (1, 1, 1):
    print("⚠️  WARNING: Your OpenSSL version is outdated!")
    print("   Solution: Reinstall Python from python.org (3.8+)")
else:
    print("✅ OpenSSL version is sufficient")

print("\nTo fix MongoDB SSL issues, run:")
print("  pip install --upgrade certifi pymongo motor urllib3")
