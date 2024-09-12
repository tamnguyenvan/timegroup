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
                Layout.fillWidth: true
                Layout.preferredHeight: 250
                spacing: 10

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
                        color: "transparent"
                        radius: 8
                        visible: spreadsheetScrollArea.visible
                    }

                    ScrollView {
                        id: spreadsheetScrollArea
                        anchors.fill: parent
                        anchors.margins: 10
                        clip: true
                        visible: false

                        // Order report spreadsheet ids
                        ColumnLayout {
                            id: orderReportSpreadsheets
                            width: parent.width
                            spacing: 10
                            visible: reportTypeCombo.currentIndex === 0

                            property var spreadsheetNames: []
                            property var spreadsheetIds: []

                            Repeater {
                                model: parent.spreadsheetNames.length
                                delegate: RowLayout {
                                    Layout.fillWidth: true
                                    property var spreadsheetName: parent.spreadsheetNames[index]
                                    property var spreadsheetId: parent.spreadsheetIds.length > index ? parent.spreadsheetIds[index] : ""

                                    Label {
                                        text: qsTr(spreadsheetName)
                                    }

                                    TextField {
                                        Layout.fillWidth: true
                                        placeholderText: spreadsheetId
                                        font.pixelSize: 14
                                        color: "#374151"
                                        background: Rectangle {
                                            implicitWidth: 500
                                            implicitHeight: 40
                                            color: "white"
                                            border.color: parent.focus ? "#4f46e5" : "#d1d5db"
                                            border.width: 1
                                            radius: 4
                                        }

                                        onTextChanged: {
                                            var shops = Object.keys(JSON.parse(JSON.stringify(modelConfig.getValue("shops"))))
                                            var key = "reports.order." + shops[index] + ".gid"

                                            console.log("key: ", key)

                                            modelConfig.setValue(key, text)
                                        }
                                    }
                                }
                            }

                            Component.onCompleted: {
                                var shopsConfig = JSON.parse(JSON.stringify(modelConfig.getValue("shops")));
                                var reportsConfig = JSON.parse(JSON.stringify(modelConfig.getValue("reports")));

                                spreadsheetNames = [];
                                spreadsheetIds = [];

                                // if (reportTypeCombo.currentIndex === 0) {
                                //     var keys = Object.keys(shopsConfig)
                                //     console.log('kkk', keys)
                                //     for (var key in shopsConfig) {
                                //         console.log('key', JSON.stringify(shopsConfig), key)
                                //         spreadsheetNames.push(shopsConfig[key] ? shopsConfig[key]["name"] : "")
                                //         spreadsheetIds.push(reportsConfig["order"][key] ? reportsConfig["order"][key]["gid"] : "")
                                //     }
                                // }

                                spreadsheetNames = [
                                    shopsConfig["2am"] ? shopsConfig["2am"]["name"] : "",
                                    shopsConfig["time_brand"] ? shopsConfig["time_brand"]["name"] : "",
                                    shopsConfig["6am_group"] ? shopsConfig["6am_group"]["name"] : "",
                                    shopsConfig["winner_group"] ? shopsConfig["winner_group"]["name"] : ""
                                ];
                                spreadsheetIds = [
                                    reportsConfig["order"]["2am"] ? reportsConfig["order"]["2am"]["gid"] || "" : "",
                                    reportsConfig["order"]["time_brand"] ? reportsConfig["order"]["time_brand"]["gid"] || "" : "",
                                    reportsConfig["order"]["6am_group"] ? reportsConfig["order"]["6am_group"]["gid"] || "" : "",
                                    reportsConfig["order"]["winner_group"] ? reportsConfig["order"]["winner_group"]["gid"] || "" : ""
                                ];
                            }
                        }

                        // Revenue report spreadsheet ids
                        ColumnLayout {
                            id: revenueReportSpreadsheets
                            width: parent.width
                            spacing: 10
                            visible: reportTypeCombo.currentIndex === 1

                            property var spreadsheetNames: []
                            property var spreadsheetIds: []

                            Repeater {
                                model: parent.spreadsheetNames.length
                                delegate: RowLayout {
                                    Layout.fillWidth: true
                                    property var spreadsheetName: parent.spreadsheetNames[index]
                                    property var spreadsheetId: parent.spreadsheetIds.length > index ? parent.spreadsheetIds[index] : ""

                                    Label {
                                        text: qsTr(spreadsheetName)
                                    }

                                    TextField {
                                        Layout.fillWidth: true
                                        placeholderText: spreadsheetId
                                        font.pixelSize: 14
                                        color: "#374151"
                                        background: Rectangle {
                                            implicitWidth: 500
                                            implicitHeight: 40
                                            color: "white"
                                            border.color: parent.focus ? "#4f46e5" : "#d1d5db"
                                            border.width: 1
                                            radius: 4
                                        }

                                        onTextChanged: {
                                            modelConfig.setValue("reports.revenue.gid", text)
                                        }
                                    }
                                }
                            }

                            Component.onCompleted: {
                                var shopsConfig = JSON.parse(JSON.stringify(modelConfig.getValue("shops")));
                                var reportsConfig = JSON.parse(JSON.stringify(modelConfig.getValue("reports")));

                                spreadsheetNames = [];
                                spreadsheetIds = [];

                                if (reportTypeCombo.currentIndex === 0) {
                                    spreadsheetNames = [
                                        "Báo cáo lợi nhuận"
                                    ];
                                    spreadsheetIds = [
                                        reportsConfig["revenue"] ? reportsConfig["revenue"]["gid"] || "" : "",
                                    ];
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
                        var timeFrame = timeFrameCombo.model[timeFrameCombo.currentIndex]
                        var reportType = reportTypeCombo.currentIndex === 0 ? "order" : "revenue"

                        if (timeFrameCombo.currentIndex === 0) {
                            timeFrame = "yesterday"
                        } else if (timeFrameCombo.currentIndex === 1) {
                            timeFrame = "last_month"
                        } else if (timeFrameCombo.currentIndex === 2) {
                            timeFrame = "last_month_and_current_month"
                        }

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

                        modelConfig.save()
                        var spreadsheetIds = []
                        if (reportTypeCombo.currentIndex === 0) {
                            spreadsheetIds = orderReportSpreadsheets.spreadsheetIds
                        } else if (reportTypeCombo.currentIndex === 1) {
                            spreadsheetIds = revenueReportSpreadsheets.spreadsheetIds
                        }
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