import QtQuick 6.7
import QtQuick.Controls 6.7
import QtQuick.Layouts 6.7
import QtQuick.Controls.Material 6.7

ApplicationWindow {
    visible: true
    width: 800
    height: 450
    x: (Screen.width - width) / 2
    y: (Screen.height - height) / 2
    title: "TimeGroup Report Studio"
    readonly property string accentColor: "#545eee"

    Material.theme: Material.Light
    Material.primary: accentColor
    Material.accent: accentColor

    Rectangle {
        anchors.fill: parent
        color: "#dbeafe"

        ColumnLayout {
            anchors.fill: parent
            spacing: 20

            Text {
                Layout.fillWidth: true
                Layout.preferredHeight: 50
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                text: qsTr("Báo cáo TimeGroup")
                font.pixelSize: 24
            }

            GridLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.topMargin: 10
                Layout.leftMargin: 20
                Layout.rightMargin: 20
                columns: 2
                rowSpacing: 20
                columnSpacing: 20

                Text {
                    text: qsTr("Loại báo cáo")
                    horizontalAlignment: Text.AlignRight
                    verticalAlignment: Text.AlignVCenter
                }
                ComboBox {
                    model: ["Báo cáo đơn hàng", "Báo cáo lợi nhuận"]
                    implicitWidth: 200
                }

                Text {
                    text: qsTr("Thời gian")
                    horizontalAlignment: Text.AlignRight
                    verticalAlignment: Text.AlignVCenter
                }
                ComboBox {
                    model: ["Hôm qua", "Tháng trước", "Tháng trước + Tháng này"]
                    implicitWidth: 200
                }

                Item { // Empty item to place the button correctly in the grid
                    Layout.columnSpan: 2
                    Layout.alignment: Qt.AlignHCenter
                    Button {
                        text: qsTr("Xuất excel")
                        width: 120
                        Material.primary: accentColor
                        Material.accent: accentColor
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                reportModel.exportReport("revenue", "yesterday")
                            }
                        }
                    }
                }
            }
        }
    }
}
