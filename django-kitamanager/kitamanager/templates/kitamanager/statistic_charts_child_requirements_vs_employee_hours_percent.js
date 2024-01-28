async function statistic_child_requirements_vs_employee_hours_percent(historydate) {

    let c = document.getElementById("statisticChildRequirementVsEmployeeHoursPercentChart");
    let ctx = c.getContext("2d");
    let statisticChildRequirementVsEmployeeHoursPercentChart = new Chart(ctx, {
        type: "bar",
        options: {
            title: {
                display: false,
                text: ""
            },
        }
    });
    let url = '{% url "kitamanager:statistic-charts-child-requirement-vs-employee-hours-percent" %}?historydate=' + historydate
    await loadChart(statisticChildRequirementVsEmployeeHoursPercentChart, url)
}

