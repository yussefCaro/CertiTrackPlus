console.log("JS cargado correctamente");

document.addEventListener("DOMContentLoaded", function () {
    const totalFormsInput = document.querySelector('input[type="hidden"][name$="TOTAL_FORMS"]');
    if (!totalFormsInput) {
        console.error("No se encontró el campo TOTAL_FORMS en el DOM.");
        return;
    }
    const formsetPrefix = totalFormsInput.name.replace('-TOTAL_FORMS', '');
    const maxForms = 3;

    const container = document.getElementById("fecha_form_container");
    const emptyFormDiv = document.getElementById("empty_form");
    const addBtn = document.getElementById("agregar_fecha_etapa2");

    if (!container) {
        console.error("No se encontró el contenedor de formularios (#fecha_form_container).");
        return;
    }
    if (!emptyFormDiv) {
        console.error("No se encontró el bloque empty_form (#empty_form).");
        return;
    }
    if (!addBtn) {
        console.error("No se encontró el botón para agregar fechas (#agregar_fecha_etapa2).");
        return;
    }

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
console.log("JS cargado correctamente");

document.addEventListener("DOMContentLoaded", function () {
    // Buscar el campo TOTAL_FORMS del formset
    const totalFormsInput = document.querySelector('input[type="hidden"][name$="TOTAL_FORMS"]');
    if (!totalFormsInput) {
        console.error("No se encontró el campo TOTAL_FORMS en el DOM. Revisa que {{ fecha_formset.management_form }} esté en el template.");
        return;
    }
    const formsetPrefix = totalFormsInput.name.replace('-TOTAL_FORMS', '');
    const maxForms = 3;

    const container = document.getElementById("fecha_form_container");
    const emptyFormDiv = document.getElementById("empty_form");
    const addBtn = document.getElementById("agregar_fecha_etapa2");

    if (!container) {
        console.error("No se encontró el contenedor de formularios (#fecha_form_container).");
        return;
    }
    if (!emptyFormDiv) {
        console.error("No se encontró el bloque empty_form (#empty_form). Revisa que {{ fecha_formset.empty_form.as_p|safe }} esté en el template.");
        return;
    }
    if (!addBtn) {
        console.error("No se encontró el botón para agregar fechas (#agregar_fecha_etapa2).");
        return;
    }

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
        // Verificar que totalFormsInput sigue existiendo antes de asignar value
        if (totalFormsInput) {
            totalFormsInput.value = forms.length;
        } else {
            console.error("No se encontró el campo TOTAL_FORMS al actualizar los índices.");
        }
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

    // Inicializa los índices al cargar la página
    updateFormIndexes();
});
