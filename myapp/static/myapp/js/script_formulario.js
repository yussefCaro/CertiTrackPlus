document.addEventListener("DOMContentLoaded", function () {
    // Detecta automáticamente el prefijo del formset
    const totalFormsInput = document.querySelector('input[type="hidden"][name$="TOTAL_FORMS"]');
    const formsetPrefix = totalFormsInput ? totalFormsInput.name.replace('-TOTAL_FORMS', '') : '';
    const maxForms = 3;

    const container = document.getElementById("fecha_form_container");
    const emptyFormDiv = document.getElementById("empty_form");
    const addBtn = document.getElementById("agregar_fecha_etapa2");

    function updateFormIndexes() {
        const forms = container.querySelectorAll(".fecha_etapa2");
        forms.forEach((form, index) => {
            form.querySelectorAll("[name]").forEach(field => {
                if (field.name) {
                    field.name = field.name.replace(new RegExp(`${formsetPrefix}-\\d+-`), `${formsetPrefix}-${index}-`);
                }
            });
            form.querySelectorAll("[id]").forEach(field => {
                if (field.id) {
                    field.id = field.id.replace(new RegExp(`${formsetPrefix}-\\d+-`), `${formsetPrefix}-${index}-`);
                }
            });
        });
        totalFormsInput.value = forms.length;
    }

    function addDeleteButton(element) {
        let deleteBtn = element.querySelector(".eliminar_fecha");
        if (!deleteBtn) {
            deleteBtn = document.createElement("button");
            deleteBtn.type = "button";
            deleteBtn.className = "eliminar_fecha btn btn-outline-danger btn-sm position-absolute top-0 end-0";
            deleteBtn.innerHTML = '<i class="bi bi-x-circle"></i>';
            deleteBtn.onclick = function () {
                element.remove();
                updateFormIndexes();
            };
            element.appendChild(deleteBtn);
        }
    }

    function addNewForm() {
        const totalForms = parseInt(totalFormsInput.value, 10);
        if (totalForms >= maxForms) {
            alert("No puedes agregar más de 3 fechas.");
            return;
        }
        let newFormHtml = emptyFormDiv.innerHTML.replace(/__prefix__/g, totalForms);
        let newElement = document.createElement("div");
        newElement.className = "fecha_etapa2 border rounded p-2 mb-2 position-relative";
        newElement.innerHTML = newFormHtml;
        addDeleteButton(newElement);
        container.appendChild(newElement);
        updateFormIndexes();
    }

    // Inicializar botones eliminar en formularios existentes
    container.querySelectorAll(".fecha_etapa2").forEach(form => addDeleteButton(form));

    addBtn.addEventListener("click", addNewForm);
});
