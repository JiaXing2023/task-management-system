// static/app.js - 独立的Vue逻辑文件
const { createApp } = Vue;

createApp({
    // 核心：自定义Vue分隔符，彻底避开Django的[[ ]]
    delimiters: ['[[', ']]'],
    data() {
        return {
            // 认证相关
            token: localStorage.getItem('token') || '',
            loginUsername: '',
            loginPassword: '',
            regUsername: '',
            regPassword: '',
            showRegister: false,
            loading: false,
            errorMsg: '',

            // 任务相关
            tasks: [],
            newTaskTitle: '',
            loadingTasks: false,
            taskError: '',

            // API基础地址（便于后续部署修改）
            apiBase: 'http://127.0.0.1:8000/api'
        };
    },
    mounted() {
        // 已登录则加载任务
        if (this.token) {
            this.loadTasks();
        }
        // 配置Axios默认请求头
        axios.defaults.headers.common['Content-Type'] = 'application/json';
        axios.defaults.timeout = 10000; // 超时时间

        // ✅ 新增：Axios全局错误处理（统一兜底，避免前端崩溃）
        axios.interceptors.response.use(
            // 成功响应直接返回
            response => response,
            // 错误响应统一处理
            error => {
                console.error('API请求错误详情：', error);
                // 1. 网络错误（无响应）
                if (!error.response) {
                    this.errorMsg = '网络错误，请检查网络连接或后端服务是否运行';
                    return Promise.reject(error);
                }
                // 2. HTTP状态码错误（4xx/5xx）
                const status = error.response.status;
                // 2.1 401未授权（token过期/无效）
                if (status === 401) {
                    this.errorMsg = '登录已过期，请重新登录';
                    this.logout(); // 自动退出登录
                }
                // 2.2 403禁止访问
                else if (status === 403) {
                    this.errorMsg = '无权限执行该操作，请联系管理员';
                }
                // 2.3 404接口不存在
                else if (status === 404) {
                    this.errorMsg = '请求的接口不存在，请检查后端路由配置';
                }
                // 2.4 500服务器错误
                else if (status >= 500) {
                    this.errorMsg = '服务器内部错误，请稍后重试';
                }
                // 其他错误交给业务逻辑处理
                return Promise.reject(error);
            }
        );
    },
    methods: {
        // 聚焦新任务输入框
        focusNewTask() {
            // ✅ 优化：避免DOM不存在时报错
            const inputEl = document.querySelector('.task-add .form-control');
            if (inputEl) inputEl.focus();
        },

        // 登录
        async login() {
            // 表单验证
            if (!this.loginUsername.trim() || !this.loginPassword.trim()) {
                this.errorMsg = '用户名和密码不能为空';
                return;
            }

            this.loading = true;
            this.errorMsg = '';
            try {
                const res = await axios.post(`${this.apiBase}/token/`, {
                    username: this.loginUsername,
                    password: this.loginPassword
                });
                this.token = res.data.access;
                localStorage.setItem('token', this.token);
                // 清空表单
                this.loginUsername = '';
                this.loginPassword = '';
                // 加载任务
                await this.loadTasks();
            } catch (err) {
                // ✅ 优化：优先取后端返回的错误，兜底用通用提示
                this.errorMsg = err.response?.data?.detail || '登录失败：用户名或密码错误';
            } finally {
                this.loading = false;
            }
        },

        // 注册
        async register() {
            // 表单验证
            if (!this.regUsername.trim()) {
                this.errorMsg = '用户名不能为空';
                return;
            }
            if (this.regPassword.length < 8) {
                this.errorMsg = '密码长度不能少于8位';
                return;
            }

            this.loading = true;
            this.errorMsg = '';
            try {
                await axios.post(`${this.apiBase}/register/`, {
                    username: this.regUsername,
                    password: this.regPassword
                });
                alert('注册成功，请使用新账号登录');
                this.showRegister = false;
                this.regUsername = '';
                this.regPassword = '';
            } catch (err) {
                // ✅ 优化：兼容后端返回的多种错误格式
                this.errorMsg = err.response?.data?.username || err.response?.data?.detail || '注册失败：用户名已存在';
            } finally {
                this.loading = false;
            }
        },

        // 退出登录
        logout() {
            if (confirm('确定要退出登录吗？')) {
                this.token = '';
                localStorage.removeItem('token');
                this.tasks = [];
                this.errorMsg = '';
                this.taskError = ''; // ✅ 新增：清空任务错误提示
            }
        },

        // 加载任务列表
        async loadTasks() {
            this.loadingTasks = true;
            this.taskError = '';
            try {
                const res = await axios.get(`${this.apiBase}/tasks/tasks/`, {
                    headers: { Authorization: `Bearer ${this.token}` }
                });
                // 兼容两种响应格式（data嵌套/直接返回数组）
                this.tasks = res.data.data || res.data;
                // 确保status字段存在（兼容后端completed映射）
                this.tasks = this.tasks.map(task => ({
                    ...task,
                    status: task.status !== undefined ? task.status : task.completed
                }));
            } catch (err) {
                // ✅ 优化：优先取全局错误处理的提示，兜底用业务提示
                this.taskError = this.errorMsg || err.response?.data?.detail || '加载任务失败，请重新登录';
                // token过期则自动退出（全局已处理，这里做双重保障）
                if (err.response?.status === 401) {
                    this.logout();
                }
            } finally {
                this.loadingTasks = false;
            }
        },

        // 添加任务
        async addTask() {
            const title = this.newTaskTitle.trim();
            if (!title) return;

            try {
                await axios.post(`${this.apiBase}/tasks/tasks/`, {
                    title: title,
                    status: false // 前端用status，后端映射为completed
                }, {
                    headers: { Authorization: `Bearer ${this.token}` }
                });
                this.newTaskTitle = '';
                await this.loadTasks(); // 重新加载列表
            } catch (err) {
                // ✅ 优化：更精准的错误提示
                const errMsg = err.response?.data?.title || err.response?.data?.detail || '添加任务失败';
                alert(errMsg);
            }
        },

        // 更新任务状态
        async updateTask(task) {
            try {
                await axios.put(`${this.apiBase}/tasks/tasks/${task.id}/`, {
                    title: task.title,
                    status: task.status
                }, {
                    headers: { Authorization: `Bearer ${this.token}` }
                });
            } catch (err) {
                // ✅ 优化：更友好的错误提示
                const errMsg = err.response?.data?.detail || '更新任务状态失败';
                alert(errMsg);
                // 回滚状态 + 重新加载
                task.status = !task.status;
                await this.loadTasks();
            }
        }
    }
}).mount('#app');