<!-- Modal Overlay -->
<div id="modal" onclick="if(event.target === this) closeModal()">
  <div class="modal-body" onclick="event.stopPropagation()">
    <!-- Top Navigation Header: <  ×  > -->
    <div class="modal-nav-header">
      <button type="button" class="nav-btn prev-btn" onclick="prevImage(); event.stopPropagation();" title="Previous">&#10094;</button>
      <button type="button" class="close-btn" onclick="closeModal(); event.stopPropagation();" title="Close">&times;</button>
      <button type="button" class="nav-btn next-btn" onclick="nextImage(); event.stopPropagation();" title="Next">&#10095;</button>
    </div>

    <div class="modal-images">
      <div class="img-box">
        <h4>PDBj MolMil Render</h4>
        <a id="modalLink" href="#" target="_blank">
          <img id="modalImg" src="" alt="PDBj Image">
        </a>
      </div>
      <div class="img-box">
        <h4>RCSB Assembly</h4>
        <a id="rcsbLink" href="#" target="_blank">
          <img id="rcsbImg" src="" alt="RCSB Assembly" class="rcsb-image">
        </a>
      </div>
    </div>

    <div class="pdbe-section">
      <h4>PDBe Views (Front / Side / Top)</h4>
      <div id="pdbeViews">
        <a id="pdbeLinkFront" href="#" target="_blank">
          <img id="pdbeFront" src="" alt="Front View">
        </a>
        <a id="pdbeLinkSide" href="#" target="_blank">
          <img id="pdbeSide" src="" alt="Side View">
        </a>
        <a id="pdbeLinkTop" href="#" target="_blank">
          <img id="pdbeTop" src="" alt="Top View">
        </a>
      </div>
    </div>

    <div class="modal-details">
      <h3 id="modalAcc"></h3>
      <div class="modal-title" id="modalTitle"></div>
      <div class="modal-links">
        <a id="linkPDBj" href="#" target="_blank" class="btn">View on PDBj</a>
        <a id="linkRCSB" href="#" target="_blank" class="btn btn-secondary">View on RCSB</a>
        <a id="linkPDBe" href="#" target="_blank" class="btn btn-secondary">View on PDBe</a>
      </div>
    </div>

    <div id="modalIndex"></div>
  </div>
</div>

<script>
const entries = [
{{IMAGE_DATA}}
];

let currentIndex = 0;

function openModal(index) {
  currentIndex = index;
  updateModal();
  document.getElementById("modal").style.display = "flex";
  document.body.style.overflow = "hidden"; // Disable background scrolling when modal is open
}

function updateModal() {
  const entry = entries[currentIndex];
  if (!entry) return;

  const pdbidLC = entry.id.toLowerCase();
  const pdbidUC = entry.id.toUpperCase();

  document.getElementById("modalAcc").textContent = pdbidUC;
  document.getElementById("modalTitle").textContent = entry.title;
  document.getElementById("modalIndex").textContent = `${currentIndex + 1} / ${entries.length}`;

  // Primary PDBj Image & Link
  document.getElementById("modalImg").src = entry.src;
  document.getElementById("modalLink").href = entry.link;
  document.getElementById("linkPDBj").href = entry.link;

  // RCSB Image & Structure Link
  const rcsbURL = `https://cdn.rcsb.org/images/structures/${pdbidLC}_assembly-1.jpeg`;
  const rcsbPage = `https://www.rcsb.org/structure/${pdbidUC}`;
  document.getElementById("rcsbImg").src = rcsbURL;
  document.getElementById("rcsbLink").href = rcsbPage;
  document.getElementById("linkRCSB").href = rcsbPage;

  // PDBe Multi-Angle Images & Entry Link
  const pdbePage = `https://www.ebi.ac.uk/pdbe/entry/pdb/${pdbidLC}`;
  document.getElementById("pdbeFront").src = `https://www.ebi.ac.uk/pdbe/static/entry/${pdbidLC}_assembly_1_chain_front_image-200x200.png`;
  document.getElementById("pdbeSide").src = `https://www.ebi.ac.uk/pdbe/static/entry/${pdbidLC}_assembly_1_chain_side_image-200x200.png`;
  document.getElementById("pdbeTop").src = `https://www.ebi.ac.uk/pdbe/static/entry/${pdbidLC}_assembly_1_chain_top_image-200x200.png`;

  document.getElementById("pdbeLinkFront").href = pdbePage;
  document.getElementById("pdbeLinkSide").href = pdbePage;
  document.getElementById("pdbeLinkTop").href = pdbePage;
  document.getElementById("linkPDBe").href = pdbePage;
}

function closeModal() {
  document.getElementById("modal").style.display = "none";
  document.body.style.overflow = "auto";
}

function nextImage() {
  currentIndex = (currentIndex + 1) % entries.length;
  updateModal();
}

function prevImage() {
  currentIndex = (currentIndex - 1 + entries.length) % entries.length;
  updateModal();
}

// Keyboard Controls
document.addEventListener("keydown", function(event) {
  if (document.getElementById("modal").style.display === "flex") {
    if (event.key === "ArrowRight") nextImage();
    if (event.key === "ArrowLeft") prevImage();
    if (event.key === "Escape") closeModal();
  }
});

// Touch / Swipe Controls for Mobile Devices
let touchStartX = 0;
let touchEndX = 0;

const modalBody = document.querySelector(".modal-body");

if (modalBody) {
  modalBody.addEventListener("touchstart", function (event) {
    touchStartX = event.changedTouches[0].screenX;
  }, { passive: true });

  modalBody.addEventListener("touchend", function (event) {
    touchEndX = event.changedTouches[0].screenX;
    handleSwipe();
  }, { passive: true });
}

function handleSwipe() {
  const swipeThreshold = 50;
  if (touchEndX < touchStartX - swipeThreshold) {
    nextImage();
  }
  if (touchEndX > touchStartX + swipeThreshold) {
    prevImage();
  }
}
</script>

