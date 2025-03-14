document.addEventListener('DOMContentLoaded', function () {
    const urlInput = document.getElementById('urlInput');
    const depthInput = document.getElementById('depthInput');
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
    const tabHistory = document.getElementById('tabHistory');
    const contentSection = document.getElementById('contentSection');
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');
    const emptyHistoryMessage = document.getElementById('emptyHistoryMessage');

    contentSection.style.display = 'block';
    websiteSection.style.display = 'none';
    historySection.style.display = 'none';
    websiteFrame.style.display = 'none';

    // Onglet "Caractéristiques"
    tabContent.addEventListener('click', function () {
        tabContent.classList.add('active');
        tabWebsite.classList.remove('active');
        tabHistory.classList.remove('active');
        contentSection.style.display = 'block';
        websiteSection.style.display = 'none';
        historySection.style.display = 'none';
        websiteFrame.style.display = 'none';
    });

    // Onglet "Site Web"
    tabWebsite.addEventListener('click', function () {
        tabWebsite.classList.add('active');
        tabContent.classList.remove('active');
        tabHistory.classList.remove('active');

        if (urlInput.value.trim() !== "") {
            websiteSection.style.display = 'block';
            contentSection.style.display = 'none';
            historySection.style.display = 'none';
            websiteFrame.style.display = 'block';
        } else {
            websiteSection.style.display = 'none';
            contentSection.style.display = 'block';
            historySection.style.display = 'none';
            websiteFrame.style.display = 'none';
        }
    });

    // Onglet "Historique"
    tabHistory.addEventListener('click', function () {
        tabHistory.classList.add('active');
        tabContent.classList.remove('active');
        tabWebsite.classList.remove('active');
        historySection.style.display = 'block';
        contentSection.style.display = 'none';
        websiteSection.style.display = 'none';
        websiteFrame.style.display = 'none';
    });

    // Action d'analyse de l'URL
    analyzeBtn.addEventListener('click', function () {
        const url = urlInput.value.trim();
        const depth = parseInt(depthInput.value, 10);

        if (url === "") {
            errorMessage.textContent = "Veuillez saisir une URL.";
            errorMessage.style.display = 'block';
            return;
        }

        errorMessage.style.display = 'none';
        results.style.display = 'none';
        graphSection.style.display = 'none';
        loading.style.display = 'block';
        analyzeBtn.disabled = true;

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
            body: JSON.stringify({ url: url, depth: depth })
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
                    // Mise à jour des statistiques
                    document.getElementById('textCount').textContent = data.content.text_count;
                    document.getElementById('imageCount').textContent = data.content.image_count;
                    document.getElementById('internalLinkCount').textContent = data.content.internal_link_count;
                    document.getElementById('externalLinkCount').textContent = data.content.external_link_count;
                    document.getElementById('videoCount').textContent = data.content.video_count;
                    document.getElementById('tableCount').textContent = data.content.table_count;
                    document.getElementById('formCount').textContent = data.content.form_count;

                    results.style.display = 'block';

                    // Mise à jour du graphe
                    if (data.graph_url) {
                        graphFrame.src = data.graph_url;
                        graphSection.style.display = 'block';
                    }

                    updateHistory(data.history);

                    // Affichage du site web dans un iframe
                    websiteFrame.src = url;
                    websiteFrame.style.display = 'block';
                }
            })
            .catch(error => {
                errorMessage.textContent = error.message;
                errorMessage.style.display = 'block';
            });
    });

    // Effacer l'historique
    clearHistoryBtn.addEventListener('click', function () {
        if (confirm('Êtes-vous sûr de vouloir vider l\'historique ?')) {
            fetch('/clear_history', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => response.json())
                .then(data => {
                    updateHistory([]);
                });
        }
    });

    function updateHistory(history) {
        historyList.innerHTML = '';
        if (history.length === 0) {
            emptyHistoryMessage.style.display = 'block';
            clearHistoryBtn.style.display = 'none';
        } else {
            emptyHistoryMessage.style.display = 'none';
            clearHistoryBtn.style.display = 'block';
            history.reverse().forEach(entry => {
                const entryDiv = document.createElement('div');
                entryDiv.className = 'history-entry';
                entryDiv.innerHTML = `
                    <a href="#" class="history-link" data-url="${entry.url}">${entry.url}</a>
                    <div class="time">Analysé le ${entry.time}</div>
                `;
                historyList.appendChild(entryDiv);
            });
        }

        // Ajouter un événement pour chaque lien d'historique
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

    // Chargement initial de l'historique
    window.onload = function () {
        fetch('/history')
            .then(response => response.json())
            .then(data => {
                updateHistory(data.history);
            });
    }

    const fullscreenBtn = document.getElementById('fullscreenBtn');

    fullscreenBtn.addEventListener('click', function () {
        if (graphFrame.requestFullscreen) {
            graphFrame.requestFullscreen();
        } else if (graphFrame.mozRequestFullScreen) { // Firefox
            graphFrame.mozRequestFullScreen();
        } else if (graphFrame.webkitRequestFullscreen) { // Chrome, Safari and Opera
            graphFrame.webkitRequestFullscreen();
        } else if (graphFrame.msRequestFullscreen) { // IE/Edge
            graphFrame.msRequestFullscreen();
        }
    });

    // Gérer la sortie du plein écran
    document.addEventListener('fullscreenchange', function () {
        if (!document.fullscreenElement) {
            fullscreenBtn.style.display = 'block'; // Réafficher le bouton quand on sort du plein écran
        }
    });
});
