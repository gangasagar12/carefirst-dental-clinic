from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Category, Post

def blog_list(request):
    categories = Category.objects.all()
    posts = Post.objects.filter(is_published=True)
    
    # Handle Search
    query = request.GET.get('q')
    if query:
        posts = posts.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(excerpt__icontains=query)
        )
        
    # Handle Category Filter
    category_slug = request.GET.get('category')
    active_category = None
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        posts = posts.filter(category=active_category)
        
    # Determine Featured Post (only show if no search/filter, or you can keep it regardless)
    # We will show it only if it's the main blog page
    featured_post = None
    if not query and not category_slug:
        featured_post = Post.objects.filter(is_published=True, is_featured=True).first()
        if featured_post:
            posts = posts.exclude(id=featured_post.id)
            
    # Popular Posts
    popular_posts = Post.objects.filter(is_published=True, is_popular=True)[:4]
    
    # Latest Posts
    latest_posts = posts[:12] # Limit to 12 for the grid

    context = {
        'categories': categories,
        'latest_posts': latest_posts,
        'featured_post': featured_post,
        'popular_posts': popular_posts,
        'active_category': active_category,
        'search_query': query,
    }
    return render(request, 'blog/blog_list.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    categories = Category.objects.all()
    # Fetch some related or popular posts for the sidebar
    popular_posts = Post.objects.filter(is_published=True, is_popular=True).exclude(id=post.id)[:4]
    
    context = {
        'post': post,
        'categories': categories,
        'popular_posts': popular_posts,
    }
    return render(request, 'blog/post_detail.html', context)
