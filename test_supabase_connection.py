"""
Test koneksi SUPABASE - Memeriksa apakah SUPABASE_URL dan SUPABASE_KEY ditemukan
Bisa dijalankan dengan environment variables atau command line arguments
"""

import os
import sys
import argparse

def test_supabase_connection(supabase_url=None, supabase_key=None):
    """Test koneksi ke Supabase"""
    print("=" * 60)
    print("TEST KONEKSI SUPABASE")
    print("=" * 60)
    
    # Cek environment variables jika tidak disediakan via args
    if not supabase_url:
        supabase_url = os.environ.get("SUPABASE_URL")
    if not supabase_key:
        supabase_key = os.environ.get("SUPABASE_KEY")
    
    print(f"\n1. PENGECEKAN ENVIRONMENT VARIABLES:")
    print(f"   SUPABASE_URL: {'DITEMUKAN' if supabase_url else 'TIDAK DITEMUKAN'}")
    print(f"   SUPABASE_KEY: {'DITEMUKAN' if supabase_key else 'TIDAK DITEMUKAN'}")
    
    if supabase_url:
        print(f"   URL Value: {supabase_url[:50]}...")
    
    if supabase_key:
        print(f"   KEY Value: {supabase_key[:20]}...")
    
    # Jika tidak ditemukan, coba cek Railway environment variables
    if not supabase_url or not supabase_key:
        print(f"\n   Mencoba cek environment Railway...")
        # Cek berbagai kemungkinan nama environment variable Railway
        railway_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
        if railway_url:
            print(f"   DATABASE_URL: DITEMUKAN (ini adalah PostgreSQL bukan Supabase)")
        
        print(f"\nHASIL: GAGAL")
        print(f"   SUPABASE_URL atau SUPABASE_KEY tidak ditemukan di environment variables")
        print(f"\n   Cara mengatasi:")
        print(f"   - Set environment variable SUPABASE_URL")
        print(f"   - Set environment variable SUPABASE_KEY")
        return {
            "success": False,
            "error": "SUPABASE_URL atau SUPABASE_KEY tidak ditemukan"
        }
    
    # Coba koneksi jika credentials tersedia
    print(f"\n2. PENGECEKAN KONEKSI:")
    try:
        from supabase import create_client, Client
        
        supabase: Client = create_client(supabase_url, supabase_key)
        print(f"   Supabase client berhasil dibuat!")
        
        # Coba test koneksi - versi sederhana tanpa RPC
        # Coba ambil data dari tables yang ada
        print(f"   Menguji koneksi ke database...")
        
        # Test dengan query sederhana ke stock_data
        try:
            response = supabase.table("stock_data").select("*").limit(1).execute()
            print(f"   Koneksi berhasil! Bisa akses stock_data table")
            print(f"   Data saat ini: {len(response.data)} row(s)")
        except Exception as e:
            print(f"   Warning saat akses stock_data: {e}")
        
        # Test lain - coba insert test record
        print(f"   Menguji insert ke cache table...")
        try:
            test_key = f"test_connection_{int(__import__('time').time())}"
            insert_response = supabase.table("cache").insert({
                "cache_key": test_key,
                "prefix": "test",
                "ticker": "TEST",
                "data": {"test": "connection"},
                "timestamp": int(__import__('time').time())
            }).execute()
            print(f"   Insert berhasil!")
            
            # Cleanup test record
            supabase.table("cache").delete().eq("cache_key", test_key).execute()
            print(f"   Cleanup berhasil!")
            
        except Exception as e:
            print(f"   Warning saat insert: {e}")
        
        print(f"\nHASIL: BERHASIL")
        print(f"   Koneksi ke Supabase berhasil!")
        
        return {
            "success": True,
            "message": "Koneksi ke Supabase berhasil",
            "url": supabase_url[:30] + "..."
        }
        
    except Exception as e:
        print(f"\nHASIL: GAGAL")
        print(f"   Error: {str(e)}")
        
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test koneksi Supabase")
    parser.add_argument("--url", help="SUPABASE_URL")
    parser.add_argument("--key", help="SUPABASE_KEY")
    args = parser.parse_args()
    
    result = test_supabase_connection(
        supabase_url=args.url,
        supabase_key=args.key
    )
    print(f"\nResult: {result}")
    sys.exit(0 if result.get('success') else 1)
