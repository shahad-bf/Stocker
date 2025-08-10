from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta


@login_required
def dashboard_view(request):
    """Main dashboard view with statistics and recent activity"""
    
    # Import models from different apps
    from products.models import Product, Category
    from suppliers.models import Supplier
    from inventory.models import StockMovement
    from notifications.models import Notification
    
    # Calculate statistics
    total_products = Product.objects.filter(is_active=True).count()
    total_categories = Category.objects.filter(is_active=True).count()
    total_suppliers = Supplier.objects.filter(is_active=True).count()
    
    # Stock statistics
    low_stock_products = Product.objects.filter(
        is_active=True,
        stock_quantity__lte=F('minimum_stock')
    ).count()
    
    out_of_stock_products = Product.objects.filter(
        is_active=True,
        stock_quantity=0
    ).count()
    
    # Calculate total inventory value
    total_value = Product.objects.filter(is_active=True).aggregate(
        total=Sum(F('stock_quantity') * F('unit_price'))
    )['total'] or 0
    
    # Recent stock movements
    recent_movements = StockMovement.objects.select_related(
        'product', 'created_by'
    ).order_by('-created_at')[:10]
    
    # Low stock alerts for sidebar
    low_stock_alerts = Product.objects.filter(
        is_active=True,
        stock_quantity__lte=F('minimum_stock')
    ).order_by('stock_quantity')[:5]
    
    # Recent notifications
    recent_notifications = Notification.objects.filter(
        Q(user=request.user) | Q(user__isnull=True)
    ).order_by('-created_at')[:5]
    
    # Unread notifications count
    unread_notifications = Notification.get_unread_count(request.user)
    
    context = {
        # Statistics
        'total_products': total_products,
        'total_categories': total_categories,
        'total_suppliers': total_suppliers,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'total_value': total_value,
        
        # Recent data
        'recent_movements': recent_movements,
        'low_stock_alerts': low_stock_alerts,
        'recent_notifications': recent_notifications,
        'unread_notifications': unread_notifications,
        
        # User info
        'user_role': request.user.profile.get_role_display() if hasattr(request.user, 'profile') else 'User',
        'user_department': request.user.profile.department if hasattr(request.user, 'profile') else 'General',
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def analytics_view(request):
    """Analytics and reports view"""
    
    from products.models import Product, Category
    from suppliers.models import Supplier
    from inventory.models import StockMovement
    
    # Time-based analytics
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Stock movements by type (last 30 days)
    movements_data = StockMovement.objects.filter(
        created_at__date__gte=month_ago
    ).values('movement_type').annotate(
        count=Count('id'),
        total_quantity=Sum('quantity')
    ).order_by('movement_type')
    
    # Products by category
    category_data = Category.objects.annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    ).order_by('-product_count')
    
    # Low stock trends
    low_stock_trend = []
    for i in range(7):
        date = today - timedelta(days=i)
        count = Product.objects.filter(
            is_active=True,
            stock_quantity__lte=F('minimum_stock')
        ).count()
        low_stock_trend.append({
            'date': date,
            'count': count
        })
    
    context = {
        'movements_data': movements_data,
        'category_data': category_data,
        'low_stock_trend': reversed(low_stock_trend),
        'total_movements_week': StockMovement.objects.filter(
            created_at__date__gte=week_ago
        ).count(),
        'total_movements_month': StockMovement.objects.filter(
            created_at__date__gte=month_ago
        ).count(),
    }
    
    return render(request, 'dashboard/analytics.html', context)


@login_required
def reports_view(request):
    """Reports view"""
    
    from products.models import Product
    from inventory.models import StockMovement
    
    # Product reports
    products_by_value = Product.objects.filter(
        is_active=True
    ).annotate(
        total_value=F('stock_quantity') * F('unit_price')
    ).order_by('-total_value')[:10]
    
    # Most active products (by stock movements)
    most_active_products = Product.objects.filter(
        is_active=True,
        stock_movements__isnull=False
    ).annotate(
        movement_count=Count('stock_movements')
    ).order_by('-movement_count')[:10]
    
    context = {
        'products_by_value': products_by_value,
        'most_active_products': most_active_products,
    }
    
    return render(request, 'dashboard/reports.html', context)