import QtQuick 6.7
import QtQuick.Controls 6.7
import QtQuick.Layouts 6.7
import QtQuick.Controls.Material 6.7

ApplicationWindow {
    id: window
    visible: true
    width: 1000
    height: 800
    minimumWidth: width
    minimumHeight: height
    maximumWidth: width
    maximumHeight: height
    title: qsTr("TimeGroup Reporter")
    Material.theme: Material.Light
    Material.accent: "#4f46e5"
    Material.primary: "#4f46e5"

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#dbeafe" }
            GradientStop { position: 1.0; color: "#e0e7ff" }
        }

        ColumnLayout {
            anchors.centerIn: parent
            width: Math.min(parent.width - 40, 600)
            spacing: 20

            Text {
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                text: qsTr("TimeGroup Reporter")
                font.pixelSize: 28
                font.bold: true
                color: "#4f46e5"
            }

            GridLayout {
                Layout.fillWidth: true
                columns: 2
                columnSpacing: 20
                rowSpacing: 20

                Text {
                    text: qsTr("Loại báo cáo")
                    font.pixelSize: 14
                    color: "#374151"
                }
                ComboBox {
                    id: reportTypeCombo
                    Layout.fillWidth: true
                    model: [qsTr("Báo cáo đơn hàng"), qsTr("Báo cáo lợi nhuận")]
                    font.pixelSize: 14
                    Material.foreground: "#374151"
                    Material.accent: "#4f46e5"
                }

                Text {
                    text: qsTr("Thời gian")
                    font.pixelSize: 14
                    color: "#374151"
                }
                ComboBox {
                    id: timeFrameCombo
                    Layout.fillWidth: true
                    model: [qsTr("Hôm qua"), qsTr("Tháng trước"), qsTr("Tháng trước + Tháng này")]
                    font.pixelSize: 14
                    Material.foreground: "#374151"
                    Material.accent: "#4f46e5"
                }
            }

            // Container for report options
            Item {
                Layout.fillWidth: true
                Layout.preferredHeight: Math.max(orderReportOptions.implicitHeight, revenueReportOptions.implicitHeight)

                // Checkbox group for order report
                ColumnLayout {
                    id: orderReportOptions
                    anchors.fill: parent
                    spacing: 10
                    visible: reportTypeCombo.currentIndex === 0

                    Text {
                        text: qsTr("Chọn báo cáo:")
                        font.pixelSize: 14
                        color: "#374151"
                    }

                    GridLayout {
                        Layout.fillWidth: true
                        columns: 3
                        rowSpacing: 10
                        columnSpacing: 20

                        CheckBox {
                            id: ghtkCheckBox
                            text: qsTr("Đơn hàng ghtk")
                            checked: true
                        }
                        CheckBox {
                            id: vtpCheckBox
                            text: qsTr("Đơn hàng vtp")
                            checked: true
                        }
                        CheckBox {
                            id: inventoryCheckBox
                            text: qsTr("Tồn kho")
                            checked: true
                        }
                        CheckBox {
                            id: waitingCheckBox
                            text: qsTr("Chờ hàng")
                            checked: true
                        }
                        CheckBox {
                            id: posCheckBox
                            text: qsTr("POS")
                            checked: true
                        }
                    }
                }

                // Checkbox group for revenue report
                ColumnLayout {
                    id: revenueReportOptions
                    anchors.fill: parent
                    spacing: 10
                    visible: reportTypeCombo.currentIndex === 1

                    Text {
                        text: qsTr("Chọn báo cáo:")
                        font.pixelSize: 14
                        color: "#374151"
                    }

                    GridLayout {
                        Layout.fillWidth: true
                        columns: 2
                        rowSpacing: 10
                        columnSpacing: 20

                        CheckBox {
                            id: revenueCheckBox1
                            text: qsTr("Đơn hàng")
                            checked: true
                        }
                        CheckBox {
                            id: revenueCheckBox2
                            text: qsTr("Chờ hàng + Tồn kho")
                            checked: true
                        }
                        CheckBox {
                            id: revenueCheckBox3
                            text: qsTr("Khu vực")
                            checked: true
                        }
                    }
                }
            }

            // Spreadsheets
            ColumnLayout {
                id: spreadsheetSettings
                Layout.fillWidth: true
                Layout.preferredHeight: 250
                spacing: 10

                property var orderReportSpreadsheets: []
                property var revenueReportSpreadsheets: []

                Component.onCompleted: {
                    loadSpreadsheetConfig()
                }

                function loadSpreadsheetConfig() {
                    var shopsConfig = JSON.parse(JSON.stringify(modelConfig.getValue("shops")));
                    var reportsConfig = JSON.parse(JSON.stringify(modelConfig.getValue("reports")));

                    orderReportSpreadsheets = [
                        {name: shopsConfig["2am"] ? shopsConfig["2am"]["name"] : "2AM", id: reportsConfig["order"]["2am"] ? reportsConfig["order"]["2am"]["gid"] || "" : "", key: "reports.order.2am.gid"},
                        {name: shopsConfig["time_brand"] ? shopsConfig["time_brand"]["name"] : "Time Brand", id: reportsConfig["order"]["time_brand"] ? reportsConfig["order"]["time_brand"]["gid"] || "" : "", key: "reports.order.time_brand.gid"},
                        {name: shopsConfig["6am_group"] ? shopsConfig["6am_group"]["name"] : "6AM Group", id: reportsConfig["order"]["6am_group"] ? reportsConfig["order"]["6am_group"]["gid"] || "" : "", key: "reports.order.6am_group.gid"},
                        {name: shopsConfig["winner_group"] ? shopsConfig["winner_group"]["name"] : "Winner Group", id: reportsConfig["order"]["winner_group"] ? reportsConfig["order"]["winner_group"]["gid"] || "" : "", key: "reports.order.winner_group.gid"}
                    ];

                    revenueReportSpreadsheets = [
                        {name: "Báo cáo lợi nhuận", id: reportsConfig["revenue"] ? reportsConfig["revenue"]["gid"] || "" : "", key: "reports.revenue.gid"}
                    ];
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Image {
                        id: toggleIcon
                        source: "qrc:/resources/icons/triangle.svg"
                        sourceSize.width: 14
                        sourceSize.height: 14
                        rotation: spreadsheetScrollArea.visible ? 90 : 0
                        Behavior on rotation {
                            NumberAnimation { duration: 200 }
                        }
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                spreadsheetScrollArea.visible = !spreadsheetScrollArea.visible
                            }
                        }
                    }

                    Text {
                        text: qsTr("Nâng cao")
                        font.pixelSize: 16
                        font.bold: true
                        color: "#374151"
                    }

                    Item {
                        Layout.fillWidth: true
                    }
                }

                Item {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 220

                    Rectangle {
                        anchors.fill: parent
                        color: "#d3dae3"
                        radius: 8
                        visible: spreadsheetScrollArea.visible
                        border.color: "#e5e7eb"
                        border.width: 1
                    }

                    ScrollView {
                        id: spreadsheetScrollArea
                        anchors.fill: parent
                        anchors.margins: 10
                        clip: true
                        visible: false

                        ColumnLayout {
                            width: parent.width
                            spacing: 15

                            Repeater {
                                model: reportTypeCombo.currentIndex === 0 ? spreadsheetSettings.orderReportSpreadsheets : spreadsheetSettings.revenueReportSpreadsheets
                                delegate: ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 10

                                    Text {
                                        text: modelData.name
                                        font.pixelSize: 14
                                        font.bold: true
                                        color: "#374151"
                                    }

                                    TextField {
                                        Layout.fillWidth: true
                                        placeholderText: modelData.id
                                        font.pixelSize: 14
                                        color: "#374151"
                                        background: Rectangle {
                                            width: parent.width
                                            implicitHeight: 40
                                            color: "white"
                                            border.color: parent.focus ? "#4f46e5" : "#d1d5db"
                                            border.width: 1
                                            radius: 4
                                        }

                                        onTextChanged: {
                                            var key = modelData.key
                                            modelConfig.setValue(key, text)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // Submit button
            Button {
                id: exportButton
                Layout.alignment: Qt.AlignHCenter
                Layout.preferredWidth: 200
                text: qsTr("Cập nhật báo cáo")
                font.pixelSize: 16
                font.bold: true
                Material.background: Material.accent
                Material.foreground: "white"
                enabled: !reportModel.isExporting

                contentItem: RowLayout {
                    spacing: 8
                    Image {
                        source: "qrc:/resources/icons/export.svg"
                        Layout.preferredWidth: 20
                        Layout.preferredHeight: 20
                    }
                    Text {
                        text: exportButton.text
                        color: exportButton.Material.foreground
                        font: exportButton.font
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        Layout.fillWidth: true
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        reportModel.log('Start exporting...', 'info')
                        var timeFrame = timeFrameCombo.model[timeFrameCombo.currentIndex]
                        var reportType = reportTypeCombo.currentIndex === 0 ? "order" : "revenue"
                        reportModel.log('11111', 'info')

                        if (timeFrameCombo.currentIndex === 0) {
                            timeFrame = "yesterday"
                        } else if (timeFrameCombo.currentIndex === 1) {
                            timeFrame = "last_month"
                        } else if (timeFrameCombo.currentIndex === 2) {
                            timeFrame = "last_month_and_current_month"
                        }
                        reportModel.log('2', 'info')

                        var selectedReports = []
                        if (reportType === "order") {
                            if (ghtkCheckBox.checked) selectedReports.push("Đơn hàng ghtk data")
                            if (vtpCheckBox.checked) selectedReports.push("Đơn hàng vtp data")
                            if (inventoryCheckBox.checked) selectedReports.push("TỒN KHO")
                            if (waitingCheckBox.checked) selectedReports.push("CHỜ HÀNG")
                            if (posCheckBox.checked) selectedReports.push("Pos data")
                        } else {
                            if (revenueCheckBox1.checked) selectedReports.push("Đơn hàng data")
                            if (revenueCheckBox2.checked) selectedReports.push("Chờ hàng + TỒN KHO")
                            if (revenueCheckBox3.checked) selectedReports.push("Khu vực data")
                        }
                        reportModel.log('3', 'info')

                        modelConfig.save()
                        reportModel.log('4', 'info')
                        var spreadsheetIds = []
                        if (reportTypeCombo.currentIndex === 0) {
                            for (var i = 0; i < spreadsheetSettings.orderReportSpreadsheets.length; ++i) {
                                spreadsheetIds.push(spreadsheetSettings.orderReportSpreadsheets[i].id)
                            }
                            reportModel.log('5', 'info')
                        } else if (reportTypeCombo.currentIndex === 1) {
                            for (var i = 0; i < spreadsheetSettings.revenueReportSpreadsheets.length; ++i) {
                                spreadsheetIds.push(spreadsheetSettings.revenueReportSpreadsheets[i].id)
                            }
                        }
                        reportModel.log('Report type: ' + reportType + ' spreadsheet ids: ' + spreadsheetIds + ' time frame: ' + timeFrame + ' selected reports: ' + selectedReports, "info")
                        reportModel.log('Exporting...', "info")
                        reportModel.exportReport(reportType, spreadsheetIds, timeFrame, selectedReports)
                    }
                }
            }

            // Message logs
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: reportModel.messageInfo
                color: "#4f46e5"
                font.pixelSize: 14
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }
        }
    }

    Component.onCompleted: {
        x = (Screen.width - width) / 2
        y = (Screen.height - height) / 2
    }
}