async function child_contract_count_by_month(historydate) {

    let c = document.getElementById("childContractCountByMonthChart");
    let ctx = c.getContext("2d");
    let childContractCountByMonthChart = new Chart(ctx, {
        type: "bar",
        options: {
            title: {
                display: false,
                text: ""
            },
        }
    });
    let url = '{% url "kitamanager:child-charts-count-by-month" %}?historydate=' + historydate
    await loadChart(childContractCountByMonthChart, url)
}

