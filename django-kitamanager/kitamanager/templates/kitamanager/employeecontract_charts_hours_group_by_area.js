async function employee_contract_hours_group_by_area(historydate) {

    let c = document.getElementById("employeeContractHoursGroupByAreaChart");
    let ctx = c.getContext("2d");
    let employeeContractHoursGroupByAreaChart = new Chart(ctx, {
        type: "pie",
        options: {
            title: {
                display: false,
                text: ""
            },
        }
    });

    let url = '{% url "kitamanager:employee-charts-hours-group-by-area" %}?historydate=' + historydate
    await loadChart(employeeContractHoursGroupByAreaChart, url)
}

window.onload = employee_contract_hours_group_by_area;
