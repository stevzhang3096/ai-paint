#!/bin/bash
# Apply i18n changes to index.html
cd /root/.openclaw/workspace/ai-paint/frontend
cp index.html index.html.i18n

# 1. Add i18n data object and switchLang function after the opening <script> tag
sed -i '/^<script>$/a\
var i18n = {\
  en: {\
    hero: "🔥 Cheapest AI Image Generator",\
    hero_highlight: "50%+ Cheaper than Competitors",\
    hero_sub: "from $0.020/shot",\
    share: "Share",\
    share_title: "Share AiCanvas",\
    generate_title: "🎨 Generate Image",\
    prompt_placeholder: "Describe the image you want...\\ne.g. a cute cat wearing a wizard hat, digital art style",\
    select_model: "📐 Select Model",\
    select_size: "📏 Select Size",\
    generate_btn: "✨ Generate",\
    signup_title: "Sign up and get",\
    signup_highlight: "10 free shots",\
    signup_sub: "Try AI image generation, no credit card needed",\
    signup_btn: "Free Sign Up →",\
    placeholder_title: "Enter a prompt and generate",\
    placeholder_text: "Input prompt, click generate",\
    history_title: "📚 History",\
    no_history: "No generations yet",\
    generating: "🎨 AI is creating...",\
    generating_overdue: "⏰ Taking longer than expected, please wait",\
    generating_timeout: "⏰ Seems stuck, click cancel and retry",\
    cancel_gen: "✕ Cancel",\
    cancelled: "✕ Cancelled, please regenerate",\
    download_btn: "⬇️ Download",\
    copy_link: "🔗 Copy Link",\
    share_btn: "𝕍 Share",\
    retry_btn: "🔄 Try Again",\
    prompt_required: "⚠️ Please enter a prompt",\
    login_required: "⚠️ Please log in first",\
    insufficient_credits: "🪙 Insufficient credits, please top up",\
    login: "Log In",\
    register: "Sign Up",\
    logout: "🚪 Log Out",\
    topup: "Top Up",\
    change_pwd: "🔒 Change Password",\
    history_menu: "📚 History",\
    orders_menu: "💰 Top Up History",\
    email_placeholder: "Email",\
    pwd_placeholder: "Password",\
    forgot_pwd: "Forgot password?",\
    send_code: "Send Code",\
    reset_pwd: "Reset Password",\
    new_pwd: "New Password (at least 4 chars)",\
    verify_code: "Enter 6-digit code",\
    enter_email: "Enter your registered email",\
    back_to_login: "← Back to Login",\
    no_account: "Don\\'t have an account? <a id=\"switchAuth\">Sign Up</a>",\
    has_account: "Already have an account? <a id=\"switchAuth\">Log In</a>",\
    forgot_title: "🔑 Forgot Password",\
    choose_payment: "💎 Choose Payment Method",\
    payment_desc: "Select payment method to top up, instant credit",\
    credit_card: "💳 Credit Card",\
    secure_payment: "Secure payment by LemonSqueezy",\
    pay_now: "Pay",\
    usdt_address: "📍 TRC-20 Address",\
    copy_addr: "📋 Copy Address",\
    txid_placeholder: "Paste TRC-20 TxID",\
    verify_btn: "🔍 Verify Payment",\
    verifying: "⏳ Checking on-chain...",\
    close: "Close",\
    cancel: "Cancel",\
    fill_all: "Please fill in all fields",\
    invalid_email: "Invalid email format",\
    pwd_too_short: "Password must be at least 4 characters",\
    verify_sent: "✅ Verification code sent",\
    pwd_reset_success: "✅ Password reset successfully, please log in",\
    login_success: "✅ Logged in successfully",\
    register_success: "✅ Registered successfully, 10 free shots awarded!",\
    download_start: "⬇️ Starting download",\
    link_copied: "✅ Link copied",\
    addr_copied: "✅ Address copied",\
    network_error: "❌ Network error",\
    confirm_delete: "Are you sure you want to delete this image?",\
    deleted: "✅ Deleted",\
    delete_failed: "❌ Delete failed",\
    orders_loading: "Loading...",\
    orders_empty: "No top up history yet",\
    orders_hint: "Click \\'Top Up\\' in the top right corner to purchase",\
    load_failed: "Load failed",\
    plans_empty: "More plans coming soon",\
    generating_failed: "❌ Generation failed",\
    payment_success: "🎉 Top up successful! +",\
    pwd_changed: "✅ Password changed successfully",\
    credits_badge: "🪙 0 shots",\
    usdt_pay: "₿ USDT TRC-20",\
    credits_left: "shots",\
    pwd_old: "Current Password",\
    pwd_new: "New Password (at least 4 chars)",\
    change_pwd_title: "🔒 Change Password",\
    pwd_modal_cancel: "Cancel",\
  },\
  zh: {\
    hero: "🔥 最便宜的图片生成网站",\
    hero_highlight: "比竞品便宜 50%+",\
    hero_sub: "低至 $0.020/张",\
    share: "分享",\
    share_title: "分享 AiCanvas",\
    generate_title: "🎨 生成图片",\
    prompt_placeholder: "描述你想要的图片，支持中英文...\\ne.g. a cute cat wearing a wizard hat, digital art style",\
    select_model: "📐 选择模型",\
    select_size: "📏 选择尺寸",\
    generate_btn: "✨ 生成",\
    signup_title: "注册即送",\
    signup_highlight: "10 张免费额度",\
    signup_sub: "免费体验 AI 图片生成，无需信用卡",\
    signup_btn: "免费注册 →",\
    placeholder_title: "输入 prompt，点击生成",\
    placeholder_text: "输入 prompt，点击生成",\
    history_title: "📚 生成历史",\
    no_history: "还没有生成记录",\
    generating: "🎨 AI 正在创作...",\
    generating_overdue: "⏰ 超过预期时间，请耐心等待",\
    generating_timeout: "⏰ 似乎超时了，请点击取消重试",\
    cancel_gen: "✕ 取消生成",\
    cancelled: "✕ 已取消，请重新生成",\
    download_btn: "⬇️ 下载图片",\
    copy_link: "🔗 复制链接",\
    share_btn: "𝕍 分享",\
    retry_btn: "🔄 再试一次",\
    prompt_required: "⚠️ 请输入 prompt",\
    login_required: "⚠️ 请先登录",\
    insufficient_credits: "🪙 额度不足，请先充值",\
    login: "登录",\
    register: "注册",\
    logout: "🚪 退出登录",\
    topup: "充值",\
    change_pwd: "🔒 修改密码",\
    history_menu: "📚 生成记录",\
    orders_menu: "💰 充值记录",\
    email_placeholder: "邮箱",\
    pwd_placeholder: "密码",\
    forgot_pwd: "忘记密码？",\
    send_code: "发送验证码",\
    reset_pwd: "重置密码",\
    new_pwd: "新密码（至少4位）",\
    verify_code: "输入6位验证码",\
    enter_email: "注册时使用的邮箱",\
    back_to_login: "← 返回登录",\
    no_account: "还没有账号？<a id=\"switchAuth\">去注册</a>",\
    has_account: "已有账号？<a id=\"switchAuth\">去登录</a>",\
    forgot_title: "🔑 找回密码",\
    choose_payment: "💎 选择充值方式",\
    payment_desc: "选择支付方式完成充值，自动到账",\
    credit_card: "💳 信用卡",\
    secure_payment: "安全支付由 LemonSqueezy 提供",\
    pay_now: "信用卡支付",\
    usdt_address: "📍 TRC-20 收款地址",\
    copy_addr: "📋 复制地址",\
    txid_placeholder: "粘贴 TRC-20 转账的 TxID",\
    verify_btn: "🔍 验证到账",\
    verifying: "⏳ 正在验证链上到账...",\
    close: "关闭",\
    cancel: "取消",\
    fill_all: "请填写完整",\
    invalid_email: "邮箱格式不正确",\
    pwd_too_short: "密码至少4位",\
    verify_sent: "验证码已发送",\
    pwd_reset_success: "✅ 密码重置成功，请重新登录",\
    login_success: "✅ 登录成功",\
    register_success: "✅ 注册成功，赠送 10 张免费额度！",\
    download_start: "⬇️ 开始下载",\
    link_copied: "✅ 链接已复制",\
    addr_copied: "✅ 地址已复制",\
    network_error: "❌ 网络错误",\
    confirm_delete: "确定删除这张图片吗？",\
    deleted: "✅ 已删除",\
    delete_failed: "❌ 删除失败",\
    orders_loading: "加载中...",\
    orders_empty: "还没有充值记录",\
    orders_hint: "点击右上角\"充值\"按钮可以购买套餐",\
    load_failed: "加载失败",\
    plans_empty: "更多套餐即将上线",\
    generating_failed: "❌ 生成失败",\
    payment_success: "🎉 充值成功！+",\
    pwd_changed: "✅ 密码修改成功",\
    credits_badge: "🪙 0 张",\
    usdt_pay: "₿ USDT TRC-20",\
    credits_left: "张",\
    pwd_old: "当前密码",\
    pwd_new: "新密码（至少4位）",\
    change_pwd_title: "🔒 修改密码",\
    pwd_modal_cancel: "取消",\
  }\
};\
var _lang = localStorage.getItem("lang") || "en";\
document.documentElement.lang = _lang;\
function t(k) { return i18n[_lang][k] || i18n.en[k] || k; }\
function switchLang(l) { _lang = l; localStorage.setItem("lang", l); document.documentElement.lang = l; document.querySelectorAll(".lang-btn").forEach(function(b){ b.classList.toggle("active", b.dataset.lang === l); }); applyI18n(); }\
function applyI18n() {\
  var m = {\
    ".i18n-hero": "hero",\
    ".i18n-hero-highlight": "hero_highlight",\
    ".i18n-hero-sub": "hero_sub",\
    ".i18n-share": "share",\
    ".i18n-share-title": "share_title",\
  };\
  for (var sel in m) { var el = document.querySelector(sel); if (el) el.textContent = t(m[sel]); }\
  applyI18nDynamic();\
}\n' index.html

echo "Step 1: i18n data object added"
