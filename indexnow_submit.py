#!/usr/bin/env python3
"""
IndexNow URL Submission Script
Submits URLs to IndexNow API for faster search engine indexing
"""

import requests
import json
import os
import sys
from pathlib import Path
from typing import List, Dict

# Configuration
SITE_URL = "https://javadbayazi.github.io"
API_KEY_FILE = "indexnow_api_key.txt"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"

# URLs to submit (add your important pages here)
URLS_TO_SUBMIT = [
    f"{SITE_URL}/",
    f"{SITE_URL}/about/",
    f"{SITE_URL}/publications/",
    f"{SITE_URL}/projects/",
    f"{SITE_URL}/cv/",
    f"{SITE_URL}/blog/",
    f"{SITE_URL}/books/",
    f"{SITE_URL}/news/mj_bayazi_AURA_EEG_Scientific_Reports/",
    f"{SITE_URL}/news/grid_mcp_space_launched/",
]


def read_api_key() -> str:
    """Read the API key from file"""
    try:
        with open(API_KEY_FILE, 'r') as f:
            api_key = f.read().strip()
        if not api_key:
            raise ValueError("API key file is empty")
        return api_key
    except FileNotFoundError:
        print(f"❌ Error: API key file '{API_KEY_FILE}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading API key: {e}")
        sys.exit(1)


def submit_urls_batch(urls: List[str], api_key: str, host: str) -> Dict:
    """
    Submit multiple URLs to IndexNow in a single request
    
    Args:
        urls: List of URLs to submit
        api_key: Your IndexNow API key
        host: Your website host
    
    Returns:
        Response data from the API
    """
    payload = {
        "host": host,
        "key": api_key,
        "urlList": urls
    }
    
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    
    try:
        response = requests.post(
            INDEXNOW_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        return {
            "status_code": response.status_code,
            "success": response.status_code in [200, 202],
            "response_text": response.text if response.text else "No response body"
        }
    except requests.exceptions.RequestException as e:
        return {
            "status_code": None,
            "success": False,
            "error": str(e)
        }


def submit_url_single(url: str, api_key: str, host: str, key_location: str) -> Dict:
    """
    Submit a single URL to IndexNow
    
    Args:
        url: URL to submit
        api_key: Your IndexNow API key
        host: Your website host
        key_location: Location of the API key file on your site
    
    Returns:
        Response data from the API
    """
    params = {
        "url": url,
        "key": api_key,
        "keyLocation": key_location
    }
    
    try:
        response = requests.get(
            INDEXNOW_ENDPOINT,
            params=params,
            timeout=30
        )
        
        return {
            "status_code": response.status_code,
            "success": response.status_code in [200, 202],
            "response_text": response.text if response.text else "No response body"
        }
    except requests.exceptions.RequestException as e:
        return {
            "status_code": None,
            "success": False,
            "error": str(e)
        }


def main():
    """Main execution function"""
    print("📖 Reading API key...")
    api_key = read_api_key()
    print(f"✅ API key loaded: {api_key[:8]}...")
    print()
    
    # Extract host from site URL
    host = SITE_URL.replace("https://", "").replace("http://", "").rstrip("/")
    key_location = f"{SITE_URL}/{API_KEY_FILE}"
    
    print(f"🌐 Host: {host}")
    print(f"🔑 Key location: {key_location}")
    print(f"📝 Submitting {len(URLS_TO_SUBMIT)} URLs...")
    print()
    
    # Submit URLs in batch
    print("📤 Batch submission:")
    result = submit_urls_batch(URLS_TO_SUBMIT, api_key, host)
    
    if result["success"]:
        print(f"✅ Batch submission successful! (Status: {result['status_code']})")
        print(f"   Response: {result['response_text']}")
        print()
        print("📋 Submitted URLs:")
        for i, url in enumerate(URLS_TO_SUBMIT, 1):
            print(f"   {i}. {url}")
    else:
        print(f"❌ Batch submission failed!")
        if "error" in result:
            print(f"   Error: {result['error']}")
        else:
            print(f"   Status: {result['status_code']}")
            print(f"   Response: {result['response_text']}")
        print()
        print("⚠️  Falling back to individual submissions...")
        print()
        
        # Try submitting individually
        success_count = 0
        fail_count = 0
        
        for i, url in enumerate(URLS_TO_SUBMIT, 1):
            print(f"📤 [{i}/{len(URLS_TO_SUBMIT)}] Submitting: {url}")
            result = submit_url_single(url, api_key, host, key_location)
            
            if result["success"]:
                print(f"   ✅ Success (Status: {result['status_code']})")
                success_count += 1
            else:
                print(f"   ❌ Failed")
                if "error" in result:
                    print(f"   Error: {result['error']}")
                else:
                    print(f"   Status: {result['status_code']}")
                fail_count += 1
            print()
        
        print(f"📊 Summary: {success_count} succeeded, {fail_count} failed")
        
        if fail_count > 0:
            sys.exit(1)
    
    print()
    print("=" * 50)
    print("🎉 IndexNow submission complete!")
    print("=" * 50)
    print()
    print("ℹ️  HTTP Status Codes:")
    print("   200 - OK: URL received successfully")
    print("   202 - Accepted: URL received successfully")
    print("   400 - Bad Request: Invalid format")
    print("   403 - Forbidden: Key validation failed")
    print("   422 - Unprocessable Entity: URL doesn't belong to the host")
    print("   429 - Too Many Requests: Rate limit exceeded")
    print()


if __name__ == "__main__":
    main()
