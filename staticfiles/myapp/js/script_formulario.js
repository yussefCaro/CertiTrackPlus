document.addEventListener("DOMContentLoaded", function () {
    let totalFormsInput = document.querySelector("#id_fechaetapa2_set-TOTAL_FORMS");
    let container = document.getElementById("fecha_form_container");
    let emptyFormHtml = container.getAttribute("data-empty-form");
    let maxForms = 3;

    function updateFormIndexes() {
        let forms = container.querySelectorAll(".fecha_etapa2");
        let visibleForms = Array.from(forms).filter(form => form.style.display !== "none");

        visibleForms.forEach((form, index) => {
            form.querySelectorAll("[name]").forEach(field => {
                let name = field.getAttribute("name");
                let id = field.getAttribute("id");

                if (name) {
                    field.setAttribute("name", name.replace(/fechaetapa2_set-\d+-/, `fechaetapa2_set-${index}-`));
                }
                if (id) {
                    field.setAttribute("id", id.replace(/fechaetapa2_set-\d+-/, `fechaetapa2_set-${index}-`));
                }
            });
        });

        totalFormsInput.value = visibleForms.length;
    }

    function addDeleteButton(element) {
    let deleteButton = element.querySelector(".eliminar_fecha");

    if (!deleteButton) {  // Solo agregar si no existe
        deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.classList.add("eliminar_fecha", "btn", "btn-danger", "btn-sm", "ms-2");
        deleteButton.innerText = "❌";

        deleteButton.onclick = function () {
            let hiddenDeleteInput = element.querySelector("input[name*='DELETE']");
            if (hiddenDeleteInput) {
                hiddenDeleteInput.checked = true;
            }
            element.style.display = "none";
            updateFormIndexes();
        };

        element.appendChild(deleteButton);
    }
}


    function addNewForm() {
        let totalForms = parseInt(totalFormsInput.value, 10);
        if (totalForms >= maxForms) {
            alert("No puedes agregar más de 3 fechas.");
            return;
        }

        let newElement = document.createElement("div");
        newElement.classList.add("fecha_etapa2", "mb-3");
        newElement.innerHTML = emptyFormHtml.replace(/__prefix__/g, totalForms);
        container.appendChild(newElement);
        addDeleteButton(newElement);

        totalFormsInput.value = totalForms + 1;
    }

    document.getElementById("agregar_fecha_etapa2").addEventListener("click", addNewForm);

    document.querySelectorAll(".fecha_etapa2").forEach(form => addDeleteButton(form));

    updateFormIndexes(); // Asegurar que los índices están bien desde el inicio
});
