// 現在の日付を表示
function updateCurrentDate() {
    const now = new Date();
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
    };
    const dateString = now.toLocaleDateString('ja-JP', options);
    const dateDisplay = document.getElementById('dateDisplay');
    if (dateDisplay) {
        dateDisplay.textContent = dateString;
    }
}

// コンテンツを更新（猫の写真 + 格言）
function refreshContent() {
    const imageElement = document.querySelector('.cat-image');
    const messageElement = document.querySelector('.daily-message');
    const refreshBtn = document.getElementById('refreshBtn');
    
    if (!imageElement || !messageElement) return;

    // ローディング表示
    imageElement.style.opacity = '0.5';
    messageElement.style.opacity = '0.5';
    refreshBtn.disabled = true;
    refreshBtn.textContent = '更新中...';
    
    fetch('/api/random_content')
        .then(response => response.json())
        .then(data => {
            if (data.cat_illustration) {
                // 新しい猫の写真を設定
                imageElement.src = `/static/uploads/${data.cat_illustration.filename}`;
                imageElement.alt = '猫の写真';
            }
            
            if (data.message) {
                // 新しい格言を設定
                messageElement.textContent = data.message;
            }
            
            // フェードイン効果
            setTimeout(() => {
                imageElement.style.opacity = '1';
                messageElement.style.opacity = '1';
                refreshBtn.disabled = false;
                refreshBtn.textContent = '更新';
            }, 300);
        })
        .catch(error => {
            console.error('コンテンツの更新に失敗しました:', error);
            imageElement.style.opacity = '1';
            messageElement.style.opacity = '1';
            refreshBtn.disabled = false;
            refreshBtn.textContent = '更新';
        });
}

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', function() {
    // 日付を更新
    updateCurrentDate();
    
    // 更新ボタンのイベントリスナーを追加
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshContent);
    }
    
    // 猫の写真のクリックで拡大表示（オプション）
    const catImage = document.querySelector('.cat-image');
    if (catImage) {
        catImage.addEventListener('click', function() {
            // モーダルで拡大表示する機能を追加できます
            console.log('猫の写真がクリックされました');
        });
    }
});

// キーボードショートカット
document.addEventListener('keydown', function(event) {
    // Rキーでコンテンツを更新
    if (event.key === 'r' || event.key === 'R') {
        refreshContent();
    }
});

// レスポンシブ対応
function handleResize() {
    const container = document.querySelector('.container');
    if (window.innerWidth <= 768) {
        container.style.padding = '15px';
    } else {
        container.style.padding = '20px';
    }
}

window.addEventListener('resize', handleResize);
handleResize(); // 初期実行
