#!/bin/bash

# ICP备案查询API Docker管理脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    echo "ICP备案查询API Docker管理脚本"
    echo ""
    echo "使用方法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  build    构建Docker镜像"
    echo "  start    启动服务"
    echo "  stop     停止服务"
    echo "  restart  重启服务"
    echo "  logs     查看日志"
    echo "  status   查看服务状态"
    echo "  clean    清理容器和镜像"
    echo "  test     测试API接口"
    echo "  help     显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 build    # 构建镜像"
    echo "  $0 start    # 启动服务"
    echo "  $0 logs     # 查看日志"
}

# 构建镜像
build_image() {
    print_info "开始构建Docker镜像..."
    docker-compose build
    print_success "镜像构建完成"
}

# 启动服务
start_service() {
    print_info "启动ICP备案查询API服务..."
    docker-compose up -d
    print_success "服务启动完成"
    print_info "API地址: http://localhost:8000"
    print_info "API文档: http://localhost:8000/docs"
    print_info "查看日志: $0 logs"
}

# 停止服务
stop_service() {
    print_info "停止服务..."
    docker-compose down
    print_success "服务已停止"
}

# 重启服务
restart_service() {
    print_info "重启服务..."
    docker-compose restart
    print_success "服务重启完成"
}

# 查看日志
show_logs() {
    print_info "显示服务日志..."
    docker-compose logs -f icp-spider-api
}

# 查看状态
show_status() {
    print_info "服务状态:"
    docker-compose ps
    echo ""
    print_info "检查API健康状态..."
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "API服务正常运行"
    else
        print_warning "API服务未响应"
    fi
}

# 清理容器和镜像
clean_up() {
    print_warning "这将删除所有相关的容器和镜像，是否继续? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_info "停止并删除容器..."
        docker-compose down --volumes --remove-orphans
        print_info "删除镜像..."
        docker rmi icp-spider_icp-spider-api 2>/dev/null || true
        print_success "清理完成"
    else
        print_info "取消清理操作"
    fi
}

# 测试API
test_api() {
    print_info "测试API接口..."
    
    # 测试健康检查
    print_info "测试健康检查接口..."
    if response=$(curl -s http://localhost:8000/health); then
        print_success "健康检查: $response"
    else
        print_error "健康检查失败"
        return 1
    fi
    
    # 测试域名查询
    print_info "测试域名查询接口..."
    test_domain="scgzyun.com"
    print_info "查询域名: $test_domain"
    
    if response=$(curl -s "http://localhost:8000/query?domain=$test_domain"); then
        if echo "$response" | grep -q '"code":200'; then
            print_success "域名查询成功"
            echo "$response" | python3 -m json.tool
        else
            print_warning "域名查询返回错误"
            echo "$response"
        fi
    else
        print_error "域名查询请求失败"
        return 1
    fi
}

# 主逻辑
case "${1:-help}" in
    build)
        build_image
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    clean)
        clean_up
        ;;
    test)
        test_api
        ;;
    help|*)
        show_help
        ;;
esac
