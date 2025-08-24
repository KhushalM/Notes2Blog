#!/usr/bin/env python3
"""
Test script for Notes2Blog graph processing
"""
import requests
import json
from pathlib import Path
import sys

def test_notes_image(image_path: str, base_url: str = "http://localhost:8000"):
    """Test the Notes2Blog pipeline with an image file"""
    
    # Check if image file exists
    if not Path(image_path).exists():
        print(f"❌ Image file not found: {image_path}")
        return False
    
    print(f"🔍 Testing with image: {image_path}")
    
    try:
        # Step 1: Upload the image
        print("📤 Uploading image...")
        with open(image_path, 'rb') as f:
            files = {'file': (Path(image_path).name, f, 'image/jpeg')}
            upload_response = requests.post(f"{base_url}/ingest", files=files)
        
        if upload_response.status_code != 200:
            print(f"❌ Upload failed: {upload_response.text}")
            return False
        
        upload_data = upload_response.json()
        image_path_key = upload_data.get('image_path')
        print(f"✅ Image uploaded successfully: {image_path_key}")
        
        # Step 2: Process the image through the graph
        print("🔄 Processing through LangGraph pipeline...")
        process_payload = {"image_path": image_path_key}
        process_response = requests.post(
            f"{base_url}/process", 
            json=process_payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if process_response.status_code != 200:
            print(f"❌ Processing failed: {process_response.text}")
            return False
        
        result = process_response.json()
        
        # Step 3: Display results
        print("\n" + "="*50)
        print("🎉 PROCESSING COMPLETED SUCCESSFULLY!")
        print("="*50)
        
        print(f"\n📝 THEME: {result.get('theme', 'N/A')}")
        
        print(f"\n📋 OUTLINE:")
        outline = result.get('outline', [])
        if outline:
            for i, item in enumerate(outline, 1):
                print(f"  {i}. {item}")
        else:
            print("  No outline generated")
        
        print(f"\n✅ VALIDATION STATUS: {'✅ Valid' if result.get('validated') else '❌ Invalid'}")
        
        print(f"\n📄 BLOG MARKDOWN LENGTH: {len(result.get('blog_markdown', ''))} characters")
        print(f"⚛️  REACT CODE LENGTH: {len(result.get('react_code', ''))} characters")
        
        # Show logs
        logs = result.get('logs', [])
        if logs:
            print(f"\n📊 PROCESSING LOGS:")
            for log in logs:
                print(f"  • {log}")
        
        # Save outputs for inspection
        if result.get('blog_markdown'):
            with open('test_output_blog.md', 'w') as f:
                f.write(result['blog_markdown'])
            print(f"\n💾 Blog markdown saved to: test_output_blog.md")
            
        if result.get('react_code'):
            with open('test_output_react.tsx', 'w') as f:
                f.write(result['react_code'])
            print(f"💾 React code saved to: test_output_react.tsx")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the server is running on http://localhost:8000")
        print("   Run: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def check_server_status(base_url: str = "http://localhost:8000"):
    """Check if the server is running"""
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print(f"JSON: {response.json()}")
            data = response.json()
            print(f"✅ Server is running!")
            print(f"   Message: {data.get('message')}")
            print(f"   OpenAI Vision: {data.get('vision')}")
            print(f"   API Key: {data.get('api_key')}")
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running")
        return False

if __name__ == "__main__":
    print("🚀 Notes2Blog Graph Tester")
    print("="*30)
    
    # Check server status first
    if not check_server_status():
        print("\n🔧 To start the server, run:")
        print("   uvicorn app.main:app --reload")
        sys.exit(1)
    
    # Get image path from command line or prompt
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = input("\n📁 Enter path to your notes image: ").strip()
    
    if not image_path:
        print("❌ No image path provided")
        sys.exit(1)
    
    # Test the image
    success = test_notes_image(image_path)
    
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n❌ Test failed!")
