document.addEventListener('DOMContentLoaded', function () {
    const urlInput = document.getElementById('urlInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const errorMessage = document.getElementById('errorMessage');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const graphSection = document.getElementById('graphSection');
    const graphFrame = document.getElementById('graphFrame');
    const historySection = document.getElementById('historySection');
    const historyList = document.getElementById('historyList');
    const websiteSection = document.getElementById('websiteSection');
    const websiteFrame = document.getElementById('websiteFrame');
    const tabContent = document.getElementById('tabContent');
    const tabWebsite = document.getElementById('tabWebsite');
    const contentSection = document.getElementById('contentSection');

    // Par défaut, afficher l'onglet contenu et cacher le site web
    contentSection.style.display = 'block';
    websiteSection.style.display = 'none';

    tabContent.addEventListener('click', function () {
        tabContent.classList.add('active');
        tabWebsite.classList.remove('active');
        contentSection.style.display = 'block';
        websiteSection.style.display = 'none';
    });

    tabWebsite.addEventListener('click', function () {
        tabWebsite.classList.add('active');
        tabContent.classList.remove('active');
        websiteSection.style.display = 'block';
        contentSection.style.display = 'none';
    });

    analyzeBtn.addEventListener('click', function () {
        errorMessage.style.display = 'none';
        results.style.display = 'none';
        graphSection.style.display = 'none';
        loading.style.display = 'block';
        analyzeBtn.disabled = true;

        const url = urlInput.value;

        if (!url.match(/^https?:\/\/.+/)) {
            errorMessage.textContent = "Veuillez entrer une URL valide.";
            errorMessage.style.display = 'block';
            loading.style.display = 'none';
            analyzeBtn.disabled = false;
            return;
        }

        fetch('/scrape', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        })
            .then(response => {
                loading.style.display = 'none';
                analyzeBtn.disabled = false;

                if (!response.ok) {
                    throw new Error('Erreur lors de l\'analyse. Veuillez réessayer.');
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    errorMessage.textContent = data.error;
                    errorMessage.style.display = 'block';
                } else {
                    document.getElementById('textCount').textContent = data.content.text_count;
                    document.getElementById('imageCount').textContent = data.content.image_count;
                    document.getElementById('internalLinkCount').textContent = data.content.internal_link_count;
                    document.getElementById('externalLinkCount').textContent = data.content.external_link_count;
                    document.getElementById('videoCount').textContent = data.content.video_count;
                    document.getElementById('tableCount').textContent = data.content.table_count;
                    document.getElementById('formCount').textContent = data.content.form_count;

                    results.style.display = 'block';

                    if (data.graph_url) {
                        graphFrame.src = data.graph_url;
                        graphSection.style.display = 'block';
                    }

                    // Mettre à jour l'historique
                    updateHistory(data.history);
                    if (data.history && data.history.length > 0) {
                        historySection.style.display = 'block';
                    } else {
                        historySection.style.display = 'none';
                    }

                    // Afficher le site web dans l'iframe
                    websiteFrame.src = url;
                }
            })
            .catch(error => {
                errorMessage.textContent = error.message;
                errorMessage.style.display = 'block';
            });
    });

    document.getElementById('clearHistoryBtn').addEventListener('click', function () {
        if (confirm('Êtes-vous sûr de vouloir vider l\'historique ?')) {
            fetch('/clear_history', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => response.json())
                .then(data => {
                    updateHistory([]);
                    historySection.style.display = 'none';
                });
        }
    });

    function updateHistory(history) {
        historyList.innerHTML = '';
        history.reverse().forEach(entry => {
            const entryDiv = document.createElement('div');
            entryDiv.className = 'history-entry';
            entryDiv.innerHTML = `
                <a href="#" class="history-link" data-url="${entry.url}">${entry.url}</a>
                <div class="time">Analysé le ${entry.time}</div>
            `;
            historyList.appendChild(entryDiv);
        });

        // Ajouter un gestionnaire d'événements aux liens de l'historique
        const historyLinks = document.querySelectorAll('.history-link');
        historyLinks.forEach(link => {
            link.addEventListener('click', function (event) {
                event.preventDefault();
                const url = this.getAttribute('data-url');
                urlInput.value = url;
                analyzeBtn.click();
            });
        });
    }

    // Charger l'historique initial
    window.onload = function () {
        fetch('/history')
            .then(response => response.json())
            .then(data => {
                updateHistory(data.history);
                if (data.history && data.history.length > 0) {
                    historySection.style.display = 'block';
                } else {
                    historySection.style.display = 'none';
                }
            });
    }
});
