const fs = require('fs');
const filePath = '/root/.openclaw/workspace/ai-paint/frontend/index.html';
let html = fs.readFileSync(filePath, 'utf8');

// Step 1: Add lang switch buttons
html = html.replace(
  '<div class="header-right">',
  `<div class="header-right">
    <div class="lang-switch">
      <button class="lang-btn active" data-lang="en" onclick="switchLang('en')">EN</button>
      <button class="lang-btn" data-lang="zh" onclick="switchLang('zh')">中</button>
    </div>`
);

// Step 2: Tag static text with i18n classes
html = html.replace(
  '<button class="btn btn-outline" id="loginBtn" onclick="showLogin()">登录</button>',
  '<button class="btn btn-outline" id="loginBtn" onclick="showLogin()"><span class="i18n-login">Log In</span></button>'
);
html = html.replace(
  '<button class="btn btn-primary" id="topupBtn" onclick="showTopup()" style="display:none">充值</button>',
  '<button class="btn btn-primary" id="topupBtn" onclick="showTopup()" style="display:none"><span class="i18n-topup">Top Up</span></button>'
);
html = html.replace(
  '<button class="user-dropdown-item" onclick="showChangePwd()">\u{1F512} 修改密码</button>',
  '<button class="user-dropdown-item" onclick="showChangePwd()">\u{1F512} <span class="i18n-change-pwd">Change Password</span></button>'
);
html = html.replace(
  '<button class="user-dropdown-item" onclick="scrollToHistory()">\u{1F4DA} 生成记录</button>',
  '<button class="user-dropdown-item" onclick="scrollToHistory()">\u{1F4DA} <span class="i18n-history-menu">History</span></button>'
);
html = html.replace(
  '<button class="user-dropdown-item" onclick="showOrders()">\u{1F4B0} 充值记录</button>',
  '<button class="user-dropdown-item" onclick="showOrders()">\u{1F4B0} <span class="i18n-orders-menu">Top Up History</span></button>'
);
html = html.replace(
  '<button class="user-dropdown-item" onclick="logout()" style="color:#f87171">\u{1F6AA} 退出登录</button>',
  '<button class="user-dropdown-item" onclick="logout()" style="color:#f87171">\u{1F6AA} <span class="i18n-logout">Log Out</span></button>'
);

html = html.replace(
  '<h1>\u{1F525} 最便宜的图片生成网站 <span class="highlight">比竞品便宜 50%+</span> <span class="sub">低至 $0.020/张</span></h1>',
  '<h1><span class="i18n-hero">\u{1F525} Cheapest AI Image Generator</span> <span class="highlight"><span class="i18n-hero-highlight">50%+ Cheaper than Competitors</span></span> <span class="sub"><span class="i18n-hero-sub">from $0.020/shot</span></span></h1>'
);
html = html.replace(
  '<span>分享</span>',
  '<span class="i18n-share">Share</span>'
);
html = html.replace(
  '<div class="sp-title">分享 AiCanvas</div>',
  '<div class="sp-title i18n-share-title">Share AiCanvas</div>'
);
html = html.replace(
  '<div class="card-title">\u{1F3A8} 生成图片</div>',
  '<div class="card-title i18n-generate-title">\u{1F3A8} Generate Image</div>'
);
html = html.replace(
  '<div class="card-label">\u{1F4D0} 选择模型</div>',
  '<div class="card-label i18n-select-model">\u{1F4D0} Select Model</div>'
);
html = html.replace(
  '<div class="card-label">\u{1F4CF} 选择尺寸</div>',
  '<div class="card-label i18n-select-size">\u{1F4CF} Select Size</div>'
);

// generate button
html = html.replace(
  '<button class="btn-generate" id="genBtn" onclick="generate()">\u2728 生成</button>',
  '<button class="btn-generate" id="genBtn" onclick="generate()"><span class="i18n-generate-btn">\u2728 Generate</span></button>'
);

// signup banner
html = html.replace(
  '<div class="sb-title">注册即送 <span class="sb-highlight">10 张</span> 免费额度</div>',
  '<div class="sb-title i18n-signup-title">Sign up and get <span class="sb-highlight i18n-signup-highlight">10 free shots</span></div>'
);
html = html.replace(
  '<div class="sb-sub">免费体验 AI 图片生成，无需信用卡</div>',
  '<div class="sb-sub i18n-signup-sub">Try AI image generation, no credit card needed</div>'
);
html = html.replace(
  '<button class="sb-btn" onclick="showRegister()">免费注册 →</button>',
  '<button class="sb-btn" onclick="showRegister()"><span class="i18n-signup-btn">Free Sign Up \u2192</span></button>'
);

// result placeholder
html = html.replace(
  '<p>输入 prompt，点击生成</p>',
  '<p class="i18n-placeholder-text">Input prompt, click generate</p>'
);

// history card title
html = html.replace(
  '<div class="card-title">\u{1F4DA} 生成历史</div>',
  '<div class="card-title i18n-history-title">\u{1F4DA} History</div>'
);

// price badge
html = html.replace(
  '<div class="pb-title">比竞品便宜 50%</div>',
  '<div class="pb-title i18n-pb-title">50% Cheaper than Competitors</div>'
);
html = html.replace(
  '<div class="pb-save">每张节省 50%+</div>',
  '<div class="pb-save i18n-pb-save">Save 50%+ per shot</div>'
);

// Step 3: Change credits badge to use dynamic i18n
html = html.replace(
  '<span class="credits-badge" id="creditsBadge">\u{1FA99} 0 张</span>',
  '<span class="credits-badge" id="creditsBadge">\u{1FA99} <span id="creditsCount">0</span> <span id="creditsUnit" class="i18n-credits-unit">shots</span></span>'
);

// Step 4: Insert i18n JS after <script>
const i18nBlock = `
// — i18n data —
const i18nData = {
  en: {
    hero: "\u{1F525} Cheapest AI Image Generator",
    hero_highlight: "50%+ Cheaper than Competitors",
    hero_sub: "from $0.020/shot",
    share: "Share", share_title: "Share AiCanvas",
    generate_title: "\u{1F3A8} Generate Image",
    select_model: "\u{1F4D0} Select Model",
    select_size: "\u{1F4CF} Select Size",
    generate_btn: "\u2728 Generate",
    signup_title: "Sign up and get",
    signup_highlight: "10 free shots",
    signup_sub: "Try AI image generation, no credit card needed",
    signup_btn: "Free Sign Up \\u2192",
    placeholder_text: "Input prompt, click generate",
    history_title: "\u{1F4DA} History",
    no_history: "No generations yet",
    generating: "\u{1F3A8} AI is creating...",
    generating_overdue: "\\u23F0 Taking longer, please wait",
    generating_timeout: "\\u23F0 Seems stuck, click cancel and retry",
    cancel_gen: "\\u2715 Cancel",
    cancelled: "\\u2715 Cancelled, please regenerate",
    download_btn: "\\u2B07\\uFE0F Download",
    copy_link: "\\u{1F517} Copy Link",
    share_btn: "\\uD835\\uDD4D Share",
    retry_btn: "\\u{1F504} Try Again",
    prompt_required: "\\u26A0\\uFE0F Please enter a prompt",
    login_required: "\\u26A0\\uFE0F Please log in first",
    insufficient_credits: "\\u{1FA99} Insufficient credits, please top up",
    login: "Log In", register: "Sign Up", logout: "\\u{1F6AA} Log Out", topup: "Top Up",
    change_pwd: "\\u{1F512} Change Password",
    history_menu: "\\u{1F4DA} History",
    orders_menu: "\\u{1F4B0} Top Up History",
    email_placeholder: "Email", pwd_placeholder: "Password",
    forgot_pwd: "Forgot password?",
    send_code: "Send Code", reset_pwd: "Reset Password",
    new_pwd: "New Password (at least 4 chars)",
    verify_code: "Enter 6-digit code",
    enter_email: "Enter your registered email",
    back_to_login: "\\u2190 Back to Login",
    forgot_title: "\\u{1F511} Forgot Password",
    choose_payment: "\\u{1F48E} Choose Payment Method",
    payment_desc: "Select payment method to top up, instant credit",
    credit_card: "\\u{1F4B3} Credit Card",
    secure_payment: "Secure payment",
    usdt_pay: "\\u20BF USDT TRC-20",
    pay_now: "Pay",
    usdt_address: "\\u{1F4CD} TRC-20 Address",
    copy_addr: "\\u{1F4CB} Copy Address",
    txid_placeholder: "Paste TRC-20 TxID",
    verify_btn: "\\u{1F50D} Verify Payment",
    verifying: "\\u23F3 Checking on-chain...",
    close: "Close", cancel: "Cancel",
    fill_all: "Please fill in all fields",
    invalid_email: "Invalid email format",
    pwd_too_short: "Password must be at least 4 characters",
    verify_sent: "Verification code sent",
    pwd_reset_success: "\\u2705 Password reset, please log in",
    login_success: "\\u2705 Logged in",
    register_success: "\\u2705 Registered! 10 free shots awarded!",
    download_start: "\\u2B07\\uFE0F Downloading",
    link_copied: "\\u2705 Link copied",
    addr_copied: "\\u2705 Address copied",
    network_error: "\\u274C Network error",
    confirm_delete: "Delete this image?",
    deleted: "\\u2705 Deleted",
    delete_failed: "\\u274C Delete failed",
    orders_loading: "Loading...",
    orders_empty: "No top up history yet",
    orders_hint: 'Click "Top Up" in top right to purchase',
    load_failed: "Load failed",
    generating_failed: "\\u274C Generation failed",
    payment_success: "\\u{1F389} Top up successful! +",
    pwd_changed: "\\u2705 Password changed",
    credits_left: "shots",
    pwd_old: "Current Password",
    pwd_new: "New Password (at least 4 chars)",
    change_pwd_title: "\\u{1F512} Change Password",
    pwd_modal_cancel: "Cancel",
    pb_save: "Save 50%+ per shot",
  },
  zh: {
    hero: "\u{1F525} 最便宜的图片生成网站",
    hero_highlight: "比竞品便宜 50%+",
    hero_sub: "低至 $0.020/张",
    share: "分享", share_title: "分享 AiCanvas",
    generate_title: "\u{1F3A8} 生成图片",
    select_model: "\u{1F4D0} 选择模型",
    select_size: "\u{1F4CF} 选择尺寸",
    generate_btn: "\u2728 生成",
    signup_title: "注册即送",
    signup_highlight: "10 张免费额度",
    signup_sub: "免费体验 AI 图片生成，无需信用卡",
    signup_btn: "免费注册 \\u2192",
    placeholder_text: "输入 prompt，点击生成",
    history_title: "\u{1F4DA} 生成历史",
    no_history: "还没有生成记录",
    generating: "\u{1F3A8} AI 正在创作...",
    generating_overdue: "\\u23F0 超过预期时间，请耐心等待",
    generating_timeout: "\\u23F0 似乎超时了，请点击取消重试",
    cancel_gen: "\\u2715 取消生成",
    cancelled: "\\u2715 已取消，请重新生成",
    download_btn: "\\u2B07\\uFE0F 下载图片",
    copy_link: "\\u{1F517} 复制链接",
    share_btn: "\\uD835\\uDD4D 分享",
    retry_btn: "\\u{1F504} 再试一次",
    prompt_required: "\\u26A0\\uFE0F 请输入 prompt",
    login_required: "\\u26A0\\uFE0F 请先登录",
    insufficient_credits: "\\u{1FA99} 额度不足，请先充值",
    login: "登录", register: "注册", logout: "\\u{1F6AA} 退出登录", topup: "充值",
    change_pwd: "\\u{1F512} 修改密码",
    history_menu: "\\u{1F4DA} 生成记录",
    orders_menu: "\\u{1F4B0} 充值记录",
    email_placeholder: "邮箱", pwd_placeholder: "密码",
    forgot_pwd: "忘记密码？",
    send_code: "发送验证码", reset_pwd: "重置密码",
    new_pwd: "新密码（至少4位）",
    verify_code: "输入6位验证码",
    enter_email: "注册时使用的邮箱",
    back_to_login: "\\u2190 返回登录",
    forgot_title: "\\u{1F511} 找回密码",
    choose_payment: "\\u{1F48E} 选择充值方式",
    payment_desc: "选择支付方式完成充值，自动到账",
    credit_card: "\\u{1F4B3} 信用卡",
    secure_payment: "安全支付",
    usdt_pay: "\\u20BF USDT TRC-20",
    pay_now: "信用卡支付",
    usdt_address: "\\u{1F4CD} TRC-20 收款地址",
    copy_addr: "\\u{1F4CB} 复制地址",
    txid_placeholder: "粘贴 TRC-20 转账的 TxID",
    verify_btn: "\\u{1F50D} 验证到账",
    verifying: "\\u23F3 正在验证链上到账...",
    close: "关闭", cancel: "取消",
    fill_all: "请填写完整",
    invalid_email: "邮箱格式不正确",
    pwd_too_short: "密码至少4位",
    verify_sent: "验证码已发送",
    pwd_reset_success: "\\u2705 密码重置成功，请重新登录",
    login_success: "\\u2705 登录成功",
    register_success: "\\u2705 注册成功，赠送 10 张免费额度！",
    download_start: "\\u2B07\\uFE0F 开始下载",
    link_copied: "\\u2705 链接已复制",
    addr_copied: "\\u2705 地址已复制",
    network_error: "\\u274C 网络错误",
    confirm_delete: "确定删除这张图片吗？",
    deleted: "\\u2705 已删除",
    delete_failed: "\\u274C 删除失败",
    orders_loading: "加载中...",
    orders_empty: "还没有充值记录",
    orders_hint: '点击右上角"充值"按钮可以购买套餐',
    load_failed: "加载失败",
    generating_failed: "\\u274C 生成失败",
    payment_success: "\\u{1F389} 充值成功！+",
    pwd_changed: "\\u2705 密码修改成功",
    credits_left: "张",
    pwd_old: "当前密码",
    pwd_new: "新密码（至少4位）",
    change_pwd_title: "\\u{1F512} 修改密码",
    pwd_modal_cancel: "取消",
    pb_save: "每张节省 50%+",
  }
};
let _lang = localStorage.getItem("lang") || "en";
document.documentElement.lang = _lang;
function t(k) {
  const d = i18nData[_lang] || i18nData.en;
  return d[k] !== undefined ? d[k] : i18nData.en[k] !== undefined ? i18nData.en[k] : k;
}
function switchLang(l) {
  _lang = l; localStorage.setItem("lang", l);
  document.documentElement.lang = l;
  document.querySelectorAll(".lang-btn").forEach(b => b.classList.toggle("active", b.dataset.lang === l));
  applyI18n();
}
function applyI18nStatic() {
  const m = {
    ".i18n-hero": "hero",
    ".i18n-hero-highlight": "hero_highlight",
    ".i18n-hero-sub": "hero_sub",
    ".i18n-share": "share",
    ".i18n-share-title": "share_title",
    ".i18n-generate-title": "generate_title",
    ".i18n-select-model": "select_model",
    ".i18n-select-size": "select_size",
    ".i18n-placeholder-text": "placeholder_text",
    ".i18n-history-title": "history_title",
    ".i18n-pb-title": "hero_highlight",
    ".i18n-pb-save": "pb_save",
    ".i18n-login": "login",
    ".i18n-register": "register",
    ".i18n-logout": "logout",
    ".i18n-topup": "topup",
    ".i18n-change-pwd": "change_pwd",
    ".i18n-history-menu": "history_menu",
    ".i18n-orders-menu": "orders_menu",
    ".i18n-signup-title": "signup_title",
    ".i18n-signup-highlight": "signup_highlight",
    ".i18n-signup-sub": "signup_sub",
    ".i18n-signup-btn": "signup_btn",
    ".i18n-generate-btn": "generate_btn",
    ".i18n-credits-unit": "credits_left",
  };
  for (const sel in m) {
    document.querySelectorAll(sel).forEach(el => { el.innerHTML = t(m[sel]); });
  }
  const pi = document.getElementById("promptInput");
  if (pi && !pi.dataset.userChanged) pi.placeholder = t("placeholder_text");
}
// — end i18n data —
`;

html = html.replace('<script>', '<script>' + i18nBlock);

// Step 5: Run applyI18n on init
html = html.replace(
  '  await checkLogin();\n})();',
  '  await checkLogin();\n  applyI18nStatic();\n})();'
);

// Step 6: After login/register
html = html.replace(
  'state.user = data.user;\n      updateUI();\n      toast(isLogin ',
  'state.user = data.user;\n      updateUI();\n      applyI18nStatic();\n      toast(isLogin '
);

html = html.replace(
  'state.user = data.user;\n    updateUI();\n  }\n}',
  'state.user = data.user;\n    updateUI();\n    applyI18nStatic();\n  }\n}'
);

html = html.replace(
  'state.user = null;\n    updateUI();\n    toast(',
  'state.user = null;\n    updateUI();\n    applyI18nStatic();\n    toast('
);

// Step 7: Replace JS hardcoded strings with t() calls
const toastReplacements = [
  ["toast('⬇️ \\u5f00\\u59cb\\u4e0b\\u8f7d')", "toast(t('download_start'), 'success')"],
  ["errorEl.textContent = '\\u8bf7\\u586b\\u5199\\u5b8c\\u6574'", "errorEl.textContent = t('fill_all')"],
  ["errorEl.textContent = '\\u90ae\\u7bb1\\u683c\\u5f0f\\u4e0d\\u6b63\\u786e'", "errorEl.textContent = t('invalid_email')"],
  ["errorEl.textContent = '\\u5bc6\\u7801\\u81f3\\u5c114\\u4f4d'", "errorEl.textContent = t('pwd_too_short')"],
  ["errorEl.textContent = '\\u8bf7\\u8f93\\u5165\\u6709\\u6548\\u90ae\\u7bb1'", "errorEl.textContent = t('invalid_email')"],
  // Generate button disabled text
  ["btn.textContent = '\\u23f3 \\u751f\\u6210\\u4e2d...'", "btn.textContent = t('generating') + '...'"],
  // Generating UI
  ["renderGeneratingUI(0);", "renderGeneratingUI(0); applyI18nStatic();"],
];

for (const [oldS, newS] of toastReplacements) {
  html = html.replace(oldS, newS);
}

// Step 8: Replace the generate button text after completion
html = html.replace(
  'btn.disabled = false;\n    btn.textContent = \'\\u2728 \\u751f\\u6210\';',
  'btn.disabled = false;\n    btn.innerHTML = t(\'generate_btn\');'
);

// Step 9: Replace toast success messages
html = html.replace(
  `toast('\\u2705 \\u767b\\u5f55\\u6210\\u529f')`,
  `toast(t('login_success'), 'success')`
);
html = html.replace(
  `toast('\\u2705 \\u6ce8\\u518c\\u6210\\u529f\\uff0c\\u8d60\\u9001 10 \\u5f20\\u514d\\u8d39\\u989d\\u5ea6\\uff01', 'success')`,
  `toast(t('register_success'), 'success')`
);
html = html.replace(
  `toast('\\u5df2\\u9000\\u51fa', 'success')`,
  `toast(t('logout'), 'success')`
);
html = html.replace(
  `toast('\\u2705 \\u5bc6\\u7801\\u4fee\\u6539\\u6210\\u529f', 'success')`,
  `toast(t('pwd_changed'), 'success')`
);
html = html.replace(
  `toast('\\u2705 \\u5df2\\u5220\\u9664', 'success')`,
  `toast(t('deleted'), 'success')`
);
html = html.replace(
  `toast('\\u2705 \\u94fe\\u63a5\\u5df2\\u590d\\u5236', 'success')`,
  `toast(t('link_copied'), 'success')`
);
html = html.replace(
  `toast('\\u2705 \\u5730\\u5740\\u5df2\\u590d\\u5236', 'success')`,
  `toast(t('addr_copied'), 'success')`
);

// Step 10: Replace other error toasts
html = html.replace(
  `toast('\\u26a0\\ufe0f \\u8bf7\\u8f93\\u5165 prompt', 'error')`,
  `toast(t('prompt_required'), 'error')`
);
html = html.replace(
  `toast('\\u26a0\\ufe0f \\u8bf7\\u5148\\u767b\\u5f55', 'error')`,
  `toast(t('login_required'), 'error')`
);
html = html.replace(
  `toast('\\ud83e\\ude99 \\u989d\\u5ea6\\u4e0d\\u8db3\\uff0c\\u8bf7\\u5148\\u5145\\u503c', 'error')`,
  `toast(t('insufficient_credits'), 'error')`
);
html = html.replace(
  `toast('\\u274c ' + (data.error || '\\u751f\\u6210\\u5931\\u8d25'), 'error')`,
  `toast('\\u274c ' + (data.error || t('generating_failed')), 'error')`
);
html = html.replace(
  `toast('\\u274c \\u7f51\\u7edc\\u9519\\u8bef', 'error')`,
  `toast(t('network_error'), 'error')`
);
html = html.replace(
  `toast('\\u274c ' + (data.error || '\\u5220\\u9664\\u5931\\u8d25'), 'error')`,
  `toast('\\u274c ' + (data.error || t('delete_failed')), 'error')`
);

// Step 11: Update credits badge dynamically
html = html.replace(
  "creditsBadge.textContent = state.user ? '\ud83e\ude99 ${state.user.credits} \u5f20' : '\ud83e\ude99 0 \u5f20';",
  'applyI18nStatic();'
);

// Remove the duplicate creditsBadge assignment right after updateUI
html = html.replace(
  "creditsBadge.textContent = state.user ? `\ud83e\ude99 ${state.user.credits} \u5f20` : '\ud83e\ude99 0 \u5f20';",
  ''
);

// Step 12: Update generate() function to use i18n in generating UI
// Replace the rendering of generating state
html = html.replace(
  `'<p style="margin-top:12px;font-size:15px">\\ud83c\\udfa8 AI \\u6b63\\u5728\\u521b\\u4f5c...</p>'`,
  `'<p style="margin-top:12px;font-size:15px">' + t('generating') + '</p>'`
);
html = html.replace(
  `'\\u23f0 \\u4f3c\\u4e4e\\u8d85\\u65f6\\u4e86\\uff0c\\u8bf7\\u70b9\\u51fb\\u53d6\\u6d88\\u91cd\\u8bd5'`,
  `t('generating_timeout')`
);
html = html.replace(
  `'\\u26a0\\ufe0f \\u8d85\\u8fc7\\u9884\\u671f\\u65f6\\u95f4\\uff0c\\u8bf7\\u8010\\u5fc3\\u7b49\\u5f85'`,
  `t('generating_overdue')`
);
html = html.replace(
  `'\\u2715 \\u53d6\\u6d88\\u751f\\u6210'`,
  `t('cancel_gen')`
);
html = html.replace(
  `'<p style="color:#6b7280">\\u2715 \\u5df2\\u53d6\\u6d88\\uff0c\\u8bf7\\u91cd\\u65b0\\u751f\\u6210</p>'`,
  `'<p style="color:#6b7280">' + t('cancelled') + '</p>'`
);

// Step 13: Update the error display in generating UI
html = html.replace(
  `'<p style="color:#f87171">' + data.error + '</p>'`,
  `'<p style="color:#f87171">' + (data.error || t('generating_failed')) + '</p>'`
);

// Step 14: Update the history no records
html = html.replace(
  `'<p style="color:#6b7280;font-size:13px;padding:8px">\\u8fd8\\u6ca1\\u6709生成记录</p>'`,
  `'<p style="color:#6b7280;font-size:13px;padding:8px">' + t('no_history') + '</p>'`
);

// Step 15: Update change password modal placeholders
html = html.replace(
  'placeholder="\\u5f53\\u524d\\u5bc6\\u7801"',
  'placeholder="Current Password"'
);
html = html.replace(
  'placeholder="\\u65b0\\u5bc6\\u7801\\uff08\\u81f3\\u5c114\\u4f4d\\uff09"',
  'placeholder="New Password (at least 4 chars)"'
);

// Step 16: Update password modal text
html = html.replace(
  "errorEl.textContent = '\\u8bf7\\u586b\\u5199\\u5b8c\\u6574'",
  "errorEl.textContent = t('fill_all')"
);
// There's another one
html = html.replace(
  "errorEl.textContent = '\\u65b0\\u5bc6\\u7801\\u81f3\\u5c114\\u4f4d'",
  "errorEl.textContent = t('pwd_too_short')"
);

// Step 17: Update order history display text
html = html.replace(
  "'<p style=\"color:#6b7280;text-align:center;padding:20px\">\\u52a0\\u8f7d\\u4e2d...</p>'",
  "'<p style=\"color:#6b7280;text-align:center;padding:20px\">' + t('orders_loading') + '</p>'"
);
html = html.replace(
  "'<p style=\"color:#f87171;text-align:center\">\\u52a0\\u8f7d\\u5931\\u8d25</p>'",
  "'<p style=\"color:#f87171;text-align:center\">' + t('load_failed') + '</p>'"
);

// Step 18: CSS for lang switch
html = html.replace('</style>', `
.lang-switch { display: flex; gap: 0; align-items: center; margin-right: 8px; }
.lang-btn { padding: 4px 10px; border: 1px solid #3b3f4f; background: transparent; color: #6b7280; cursor: pointer; font-size: 12px; font-weight: 600; transition: all .15s; line-height: 1.4; }
.lang-btn:first-child { border-radius: 6px 0 0 6px; }
.lang-btn:last-child { border-radius: 0 6px 6px 0; }
.lang-btn.active { background: #2e1065; border-color: #8b5cf6; color: #a78bfa; }
.lang-btn:hover:not(.active) { border-color: #6b7280; color: #9ca3af; }
</style>`);

// Step 19: Fix the modal showLogin texts
html = html.replace(
  "document.getElementById('modalTitle').textContent = isLogin ? '\u767b\u5f55' : '\u6ce8\u518c';",
  "document.getElementById('modalTitle').textContent = isLogin ? t('login') : t('register');"
);
html = html.replace(
  "document.getElementById('modalActionBtn').textContent = isLogin ? '\u767b\u5f55' : '\u6ce8\u518c';",
  "document.getElementById('modalActionBtn').textContent = isLogin ? t('login') : t('register');"
);
html = html.replace(
  "document.getElementById('switchText').innerHTML = isLogin\n    ? '\u8fd8\u6ca1\u6709\u8d26\u53f7\uff1f<a id=\"switchAuth\">\u53bb\u6ce8\u518c</a>'\n    : '\u5df2\u6709\u8d26\u53f7\uff1f<a id=\"switchAuth\">\u53bb\u767b\u5f55</a>';",
  "document.getElementById('switchText').innerHTML = isLogin ? t('no_account') : t('has_account');"
);

// Step 20: Forgot password link
html = html.replace(
  "if (forgotLink) forgotLink.onclick = showForgotPwd;",
  "if (forgotLink) { forgotLink.onclick = showForgotPwd; forgotLink.textContent = t('forgot_pwd'); }"
);

// Step 21: Verify code toast
html = html.replace(
  "toast(data.message || '\u9a8c\u8bc1\u7801\u5df2\u53d1\u9001', 'success')",
  "toast(data.message || t('verify_sent'), 'success')"
);

// Step 22: Reset password toast
html = html.replace(
  "toast('\u2705 \u5bc6\u7801\u91cd\u7f6e\u6210\u529f\uff0c\u8bf7\u91cd\u65b0\u767b\u5f55', 'success')",
  "toast(t('pwd_reset_success'), 'success')"
);

// Step 23: Confirm delete
html = html.replace(
  "if (!confirm('\u786e\u5b9a\u5220\u9664\u8fd9\u5f20\u56fe\u7247\u5417\uff1f')) return;",
  "if (!confirm(t('confirm_delete'))) return;"
);

// Step 24: Toast for generation success
html = html.replace(
  "toast('\u2705 \u751f\u6210\u6210\u529f\uff01', 'success')",
  "toast(t('login
