#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT
    
public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();
    
private slots:
    void on_update_clicked();

    void on_enable_clicked();

    void on_stop_clicked();

private:
    Ui::MainWindow *ui;
};

#endif // MAINWINDOW_H
