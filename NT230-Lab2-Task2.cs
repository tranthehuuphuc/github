using System;
using System.Diagnostics;
using System.IO;
using System.ServiceProcess;
using System.Timers;

namespace NT230_Lab2_Task2
{
    public partial class Service1 : ServiceBase
    {
        System.Timers.Timer timer = new Timer();
        string processName = "notepad"; // Tên process cần kiểm tra
        int checkInterval = 10000; // Kiểm tra mỗi 10 giây

        public Service1()
        {
            InitializeComponent();
        }

        protected override void OnStart(string[] args)
        {
            WriteToFile("Service started at " + DateTime.Now);
            timer.Elapsed += new ElapsedEventHandler(OnElapsedTime);
            timer.Interval = checkInterval;
            timer.Enabled = true;
        }

        protected override void OnStop()
        {
            WriteToFile("Service stopped at " + DateTime.Now);
        }

        private void OnElapsedTime(object source, ElapsedEventArgs e)
        {
            DateTime now = DateTime.Now;
            int hour = now.Hour;
            Process[] pname = Process.GetProcessesByName(processName);

            if (hour >= 9 && hour < 18) // Trong khoảng 9h - 18h
            {
                if (pname.Length == 0) // Nếu process không chạy → Bật lên
                {
                    WriteToFile($"{processName} not running. Starting...");
                    Process.Start(processName + ".exe");
                }
                else // Nếu process đang chạy → Ghi log
                {
                    WriteToFile($"{processName} is already running.");
                }
            }
            else // Ngoài khung giờ 9h - 18h
            {
                if (pname.Length > 0) // Nếu process đang chạy → Tắt đi
                {
                    WriteToFile($"{processName} is running outside schedule. Stopping...");
                    foreach (Process p in pname)
                    {
                        p.Kill();
                    }
                }
                else // Nếu process không chạy → Ghi log
                {
                    WriteToFile($"{processName} is not running outside schedule.");
                }
            }
        }

        private void WriteToFile(string message)
        {
            string path = AppDomain.CurrentDomain.BaseDirectory + "\\Logs";
            if (!Directory.Exists(path))
            {
                Directory.CreateDirectory(path);
            }
            string filepath = path + "\\ServiceLog.txt";
            using (StreamWriter sw = File.AppendText(filepath))
            {
                sw.WriteLine(DateTime.Now + ": " + message);
            }
        }
    }
}
