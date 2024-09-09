import QtQuick 6.7
import QtQuick.Controls 6.7
import QtQuick.Layouts 6.7
import QtQuick.Controls.Material 6.7

ApplicationWindow {
    id: window
    visible: true
    width: 800
    height: 600
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

            // Checkbox group for order report
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 10
                visible: reportTypeCombo.currentIndex === 0

                Text {
                    text: qsTr("Chọn báo cáo:")
                    font.pixelSize: 14
                    color: "#374151"
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

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
                        text: qsTr("TỒN KHO")
                        checked: true
                    }
                    CheckBox {
                        id: waitingCheckBox
                        text: qsTr("CHỜ HÀNG")
                        checked: true
                    }
                    CheckBox {
                        id: posCheckBox
                        text: qsTr("Pos")
                        checked: true
                    }
                }
            }

            // Checkbox group for profit report
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 10
                visible: reportTypeCombo.currentIndex === 1

                Text {
                    text: qsTr("Chọn báo cáo:")
                    font.pixelSize: 14
                    color: "#374151"
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    CheckBox {
                        id: profitCheckBox1
                        text: qsTr("Đơn hàng")
                        checked: true
                    }
                    CheckBox {
                        id: profitCheckBox2
                        text: qsTr("Chờ hàng + TỒN KHO")
                        checked: true
                    }
                    CheckBox {
                        id: profitCheckBox3
                        text: qsTr("Khu vực")
                        checked: true
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
                enabled: reportModel.isExporting === false

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
                            if (ghtkCheckBox.checked) selectedReports.push(ghtkCheckBox.text)
                            if (vtpCheckBox.checked) selectedReports.push(vtpCheckBox.text)
                            if (inventoryCheckBox.checked) selectedReports.push(inventoryCheckBox.text)
                            if (waitingCheckBox.checked) selectedReports.push(waitingCheckBox.text)
                            if (posCheckBox.checked) selectedReports.push(posCheckBox.text)
                        } else {
                            if (profitCheckBox1.checked) selectedReports.push("profit1")
                            if (profitCheckBox2.checked) selectedReports.push("profit2")
                            if (profitCheckBox3.checked) selectedReports.push("profit3")
                        }

                        reportModel.exportReport(reportType, timeFrame, selectedReports)
                    }
                }
            }

            // Message logs
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: qsTr(reportModel.messageInfo)
                color: "#4f46e5"
                font.pixelSize: 14
            }
        }
    }

    Component.onCompleted: {
        x = (Screen.width - width) / 2
        y = (Screen.height - height) / 2
    }
}