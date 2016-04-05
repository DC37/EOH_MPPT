#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <sys/types.h>
#include <unistd.h>
#include <X11/Xlib.h>

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    ui->stop->hide();
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::on_update_clicked()
{
    QString voltage2 = ui->voltage->toPlainText();
    std::ofstream myfile;
    myfile.open("flag.dat", std::ios::trunc);
    myfile << voltage2.toStdString();
    myfile.close();
}

void MainWindow::on_enable_clicked()
{
    ui->enable->hide();
    ui->stop->show();
    system("python mppt.py &\n");
}

void MainWindow::on_stop_clicked()
{
    ui->stop->hide();
    ui->enable->show();
    system("./kill.sh");
}
