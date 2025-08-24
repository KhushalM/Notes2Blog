# Quick Start Guide: Portfolio Integration

## Immediate Next Steps

### 1. Test the Enhanced Agent
```bash
# Test the new metadata generation
cd /Users/khushal/Documents/GitHub/Notes2Blog
python -m uvicorn app.main:app --reload

# Upload a test image and check the response
# You should now see metadata in the response
```

### 2. Create a Simple Portfolio Integration

Create a new file `portfolio_example.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>My Portfolio - Blog Creator</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <div class="container mx-auto p-8">
        <h1 class="text-4xl font-bold mb-8">Create Blog from Notes</h1>
        
        <div class="bg-white rounded-lg shadow-md p-6">
            <input type="file" id="imageInput" accept="image/*" class="mb-4">
            <button onclick="processBlog()" class="bg-blue-500 text-white px-4 py-2 rounded">
                Process Notes
            </button>
            
            <div id="status" class="mt-4"></div>
            <div id="result" class="mt-8"></div>
        </div>
    </div>

    <script>
        async function processBlog() {
            const fileInput = document.getElementById('imageInput');
            const file = fileInput.files[0];
            if (!file) return;

            const statusDiv = document.getElementById('status');
            const resultDiv = document.getElementById('result');
            
            statusDiv.innerHTML = 'Uploading image...';
            
            // Upload image
            const formData = new FormData();
            formData.append('file', file);
            
            const uploadResponse = await fetch('http://localhost:8000/ingest', {
                method: 'POST',
                body: formData
            });
            
            const { image_path } = await uploadResponse.json();
            
            statusDiv.innerHTML = 'Processing notes...';
            
            // Process image
            const processResponse = await fetch('http://localhost:8000/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image_path })
            });
            
            const result = await processResponse.json();
            
            statusDiv.innerHTML = 'Complete!';
            
            // Display results
            resultDiv.innerHTML = `
                <h2 class="text-2xl font-bold mb-4">${result.metadata.title}</h2>
                <p class="text-gray-600 mb-4">${result.metadata.summary}</p>
                <div class="flex gap-2 mb-4">
                    ${result.metadata.tags.map(tag => 
                        `<span class="bg-blue-100 text-blue-800 px-2 py-1 rounded">${tag}</span>`
                    ).join('')}
                </div>
                <div class="prose max-w-none">
                    ${result.blog_markdown}
                </div>
            `;
        }
    </script>
</body>
</html>
```

### 3. Deploy Your Agent (Quick Method)

Using **Railway** (easiest):
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and initialize
railway login
railway init

# Deploy
railway up
```

Using **Render**:
1. Push your code to GitHub
2. Connect to Render
3. Create new Web Service
4. Set environment variables
5. Deploy

### 4. Create Portfolio Blog Component

For React/Next.js portfolio:

```jsx
// components/BlogFromNotes.jsx
import { useState } from 'react';

export function BlogFromNotes() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [blog, setBlog] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    
    try {
      // Upload to your deployed API
      const formData = new FormData();
      formData.append('file', file);
      
      const uploadRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/ingest`, {
        method: 'POST',
        body: formData,
      });
      
      const { image_path } = await uploadRes.json();
      
      // Process the image
      const processRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_path }),
      });
      
      const blogData = await processRes.json();
      setBlog(blogData);
      
      // Save to your database here
      // await saveBlogPost(blogData);
      
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">
            Upload Handwritten Notes
          </label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setFile(e.target.files[0])}
            className="w-full"
          />
        </div>
        
        <button
          type="submit"
          disabled={!file || loading}
          className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          {loading ? 'Processing...' : 'Create Blog Post'}
        </button>
      </form>
      
      {blog && (
        <div className="mt-8">
          <h2 className="text-2xl font-bold">{blog.metadata.title}</h2>
          <p className="text-gray-600">{blog.metadata.summary}</p>
          <div className="prose mt-4" 
            dangerouslySetInnerHTML={{ __html: blog.blog_markdown }} 
          />
        </div>
      )}
    </div>
  );
}
```

### 5. Add to Your Portfolio Routes

```jsx
// pages/blog/create.js or app/blog/create/page.tsx
import { BlogFromNotes } from '@/components/BlogFromNotes';

export default function CreateBlogPage() {
  return (
    <div>
      <h1>Create Blog from Handwritten Notes</h1>
      <BlogFromNotes />
    </div>
  );
}
```

## What You've Gained

1. ✅ **Metadata Generation** - SEO-friendly titles, summaries, and tags
2. ✅ **Better Structure** - Organized outputs with JSON metadata
3. ✅ **Portfolio-Ready API** - Returns all necessary data for integration
4. ✅ **Extensible Design** - Easy to add more features

## Next Development Priority

1. **Database Integration** - Store blogs permanently
2. **Image Storage** - Save original notes with blogs  
3. **Edit Interface** - Allow post-generation edits
4. **Style Customization** - Match your portfolio design

Start with the test, then move to the simple HTML example, and gradually integrate into your portfolio framework!
