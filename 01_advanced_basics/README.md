# ���������� �����
������ ����������� ngnix-���� ������� ��������� ������ ������� "��������������" url

## ��� ����:
* ����� ����: nginx-access-ui.log-20170630.gz
* ������ �������� ����� ���������� ������������� �������� ������
* ���� ����� ���� � plain � gzip

## ��� �����:
* count - ������� ��� ����������� URL, ���������� ��������
* count_perc - ������� ��� ����������� URL, � ���������� ������������ ������ ����� ��������
* time_sum - ��������� $request_time ��� ������� URL'�, ���������� ��������
* time_perc - ��������� $request_time ��� ������� URL'�, � ��������� ������������ ������ $request_time ���� ��������
* time_avg - ������� $request_time ��� ������� URL'�
* time_max - ������������ $request_time ��� ������� URL'a
* time_med - ������� $request_time ��� ������� URL'�

## �������� ����������������:
1. ������ ������������ ��� ������� ��������� (�� ����� ������ ����� � �����) ��� �
LOG_DIR. 
  * ������ ���; 
  * ������ ������ ����; 
  * ������� ����������� ���������� �� url'��;
  * �������� ������ report.html. 
2. ������� ������ ����� � REPORT_DIR . � ����� �������� REPORT_SIZE URL'�� � ���������� ��������� �������� ��������� (time_sum).
3. ������� �������� ������� ������� ������ �� ������� �����, ������� ��� ���� ����� --config.