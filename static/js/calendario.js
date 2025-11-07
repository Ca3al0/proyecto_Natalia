const modal = document.getElementById("eventModal");
const modalTitle = document.getElementById("modalTitle");
const modalBody = document.getElementById("modalBody");
const registroModal = document.getElementById("registroFotograficoModal");

function openModal(title, body){
    modalTitle.textContent = title;
    modalBody.innerHTML = body;
    modal.style.display = "block";
}
function closeModal(){ modal.style.display = "none"; }

function abrirRegistroFotografico(idEvento){
    registroModal.style.display = 'block';
    document.getElementById('registroFotograficoForm').reset();
    document.getElementById('registroPreview').style.display = 'none';
    document.getElementById('registroFotograficoForm').style.display = 'block';
}

function cerrarRegistro(){ registroModal.style.display = 'none'; }

window.onclick = function(event){
    if(event.target == modal) closeModal();
    if(event.target == registroModal) cerrarRegistro();
}

document.addEventListener('DOMContentLoaded', function(){
    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView:'dayGridMonth',
        locale:'es',
        headerToolbar:{left:'prev,next today', center:'title', right:'dayGridMonth,timeGridWeek,timeGridDay'},
        events:{
            url:'/transportista/api/calendario',
            failure:function(){ openModal('Error','No se pudieron cargar los eventos del calendario'); }
        },
        eventClick:function(info){
            const tipo = (info.event.extendedProps.tipo || 'Evento').toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"");
            const usuario = info.event.extendedProps.usuario || 'Desconocido';
            const location = info.event.extendedProps.location || 'Ubicación no especificada';
            const title = info.event.title || 'Sin título';
            const idEvento = info.event.id || '';

            let body = `<p><strong>Tipo:</strong> ${tipo}</p>
                        <p><strong>Evento:</strong> ${title}</p>
                        <p><strong>Cliente:</strong> ${usuario}</p>
                        <p><strong>Ubicación:</strong> ${location}</p>`;

            if(tipo === 'instalacion'){
                body += `<div style="margin-top:15px; text-align:center;">
                            <button class="modal-footer-btn" onclick="abrirRegistroFotografico('${idEvento}')">Registro Fotográfico</button>
                         </div>`;
            }

            openModal(title, body);
        },
        eventDidMount:function(info){
            const tipo = (info.event.extendedProps.tipo || '').toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"");
            info.el.dataset.tipo = tipo;
            info.el.style.cursor = 'pointer';
        }
    });
    calendar.render();
});


document.getElementById('registroFotograficoForm').addEventListener('submit', function(e){
    e.preventDefault();
    const form = e.target;
    const fotosAntes = form.querySelector('input[name="fotos_antes"]').files;
    const fotosDespues = form.querySelector('input[name="fotos_despues"]').files;
    const descAntes = form.querySelector('textarea[name="desc_antes"]').value.trim();
    const descDespues = form.querySelector('textarea[name="desc_despues"]').value.trim();

    // Validación
    if(fotosAntes.length === 0 || fotosDespues.length === 0 || !descAntes || !descDespues){
        alert("Por favor, completa todos los campos antes de guardar el registro.");
        return;
    }

    const contAntes = document.getElementById('imagenesAntes');
    contAntes.innerHTML = '';
    for(let i = 0; i < fotosAntes.length; i++){
        const img = document.createElement('img');
        img.src = URL.createObjectURL(fotosAntes[i]);
        img.style.maxWidth = '100px';
        img.style.marginRight = '5px';
        img.style.marginBottom = '5px';
        contAntes.appendChild(img);
    }
    document.getElementById('descripcionAntes').textContent = descAntes;

    const contDespues = document.getElementById('imagenesDespues');
    contDespues.innerHTML = '';
    for(let i = 0; i < fotosDespues.length; i++){
        const img = document.createElement('img');
        img.src = URL.createObjectURL(fotosDespues[i]);
        img.style.maxWidth = '100px';
        img.style.marginRight = '5px';
        img.style.marginBottom = '5px';
        contDespues.appendChild(img);
    }
    document.getElementById('descripcionDespues').textContent = descDespues;

    form.style.display = 'none';
    document.getElementById('registroPreview').style.display = 'block';
});
