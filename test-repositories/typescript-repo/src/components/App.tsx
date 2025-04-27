import React, { useState, useEffect } from 'react';
import Header from './Header';
import Footer from './Footer';
import Card from './common/Card';
import Button from './common/Button';
import Input from './common/Input';
import { useForm } from '../hooks/useForm';
import { useApi } from '../hooks/useApi';
import { postApi } from '../services/api';
import { Post } from '../types';
import { truncateText, formatDate } from '../utils/helpers';

/**
 * Main App component
 */
const App: React.FC = () => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [selectedPost, setSelectedPost] = useState<Post | null>(null);
  
  // Use our custom API hook
  const { loading, error, execute: fetchPosts } = useApi<Post[]>(postApi.getPosts);
  
  // Use our custom form hook
  const { values, handleChange, handleSubmit, errors } = useForm({
    initialValues: {
      title: '',
      content: '',
      tags: '',
    },
    onSubmit: async (formValues) => {
      try {
        const tags = formValues.tags.toString().split(',').map(tag => tag.trim());
        
        // Creating a new post
        const response = await postApi.createPost({
          title: formValues.title.toString(),
          content: formValues.content.toString(),
          userId: '1', // In a real app, this would be the current user's ID
          tags,
          createdAt: new Date(),
          updatedAt: new Date(),
        });
        
        if (response.success && response.data) {
          setPosts([response.data, ...posts]);
        }
      } catch (error) {
        console.error('Failed to create post:', error);
      }
    },
  });
  
  // Load posts on component mount
  useEffect(() => {
    const loadPosts = async () => {
      const response = await fetchPosts();
      if (response.success && response.data) {
        setPosts(response.data);
      }
    };
    
    loadPosts();
  }, [fetchPosts]);
  
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-grow container mx-auto px-4 py-6">
        <div className="grid grid-cols-12 gap-6">
          {/* Post creation form */}
          <div className="col-span-12 md:col-span-4">
            <Card title="Create New Post">
              <form onSubmit={handleSubmit}>
                <Input
                  id="title"
                  name="title"
                  label="Title"
                  value={values.title as string}
                  onChange={handleChange}
                  error={errors.title}
                  required
                />
                
                <div className="mb-4">
                  <label htmlFor="content" className="block mb-2 text-sm font-medium text-gray-700">
                    Content <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    id="content"
                    name="content"
                    value={values.content as string}
                    onChange={handleChange}
                    rows={5}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 transition-colors ${
                      errors.content ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-gray-300 focus:border-blue-500 focus:ring-blue-200'
                    }`}
                    required
                  />
                  {errors.content && (
                    <p className="mt-1 text-sm text-red-600">{errors.content}</p>
                  )}
                </div>
                
                <Input
                  id="tags"
                  name="tags"
                  label="Tags (comma-separated)"
                  value={values.tags as string}
                  onChange={handleChange}
                  placeholder="tech, news, tutorial"
                />
                
                <Button type="submit" fullWidth>
                  Create Post
                </Button>
              </form>
            </Card>
          </div>
          
          {/* Posts list */}
          <div className="col-span-12 md:col-span-8">
            <h2 className="text-2xl font-bold mb-4">Recent Posts</h2>
            
            {loading ? (
              <div className="text-center py-4">Loading posts...</div>
            ) : error ? (
              <div className="text-center py-4 text-red-600">
                Error loading posts: {error}
              </div>
            ) : posts.length === 0 ? (
              <div className="text-center py-4 text-gray-600">
                No posts found. Create your first post!
              </div>
            ) : (
              <div className="space-y-4">
                {posts.map((post) => (
                  <Card 
                    key={post.id}
                    className="hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => setSelectedPost(post)}
                  >
                    <h3 className="text-xl font-semibold">{post.title}</h3>
                    <p className="text-gray-500 text-sm mt-1">
                      Posted on {formatDate(post.createdAt)}
                    </p>
                    <p className="mt-2 text-gray-600">
                      {truncateText(post.content, 150)}
                    </p>
                    {post.tags.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-1">
                        {post.tags.map((tag, index) => (
                          <span 
                            key={index}
                            className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default App; 