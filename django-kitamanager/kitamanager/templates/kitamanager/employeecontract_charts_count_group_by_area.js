async function employee_contract_count_group_by_area(historydate) {

    let c = document.getElementById("employeeContractCountGroupByAreaChart");
    let ctx = c.getContext("2d");
    let employeeContractCountGroupByAreaChart = new Chart(ctx, {
        type: "pie",
        options: {
            title: {
                display: false,
                text: ""
            },
        }
    });
    let url = '{% url "kitamanager:employee-charts-count-group-by-area" %}?historydate=' + historydate
    await loadChart(employeeContractCountGroupByAreaChart, url)
}

