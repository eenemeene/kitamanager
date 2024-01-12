async function child_contract_pay_income_vs_invoice(historydate) {

    let c = document.getElementById("childContractPayIncomeVsInvoiceChart");
    let ctx = c.getContext("2d");
    let childContractPayIncomeVsInvoiceChart = new Chart(ctx, {
        type: "bar",
        options: {
            title: {
                display: false,
                text: ""
            },
        }
    });
    let url = '{% url "kitamanager:child-charts-pay-income-vs-invoice" %}?historydate=' + historydate
    await loadChart(childContractPayIncomeVsInvoiceChart, url)
}

