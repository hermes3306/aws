import os
import xml.etree.ElementTree as ET
import csv
from datetime import datetime

def gpx_to_csv(gpx_file, csv_file):
    tree = ET.parse(gpx_file)
    root = tree.getroot()

    # GPX 네임스페이스 정의
    ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}

    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['x', 'y', 'd', 't'])  # CSV 헤더 작성

        for trkpt in root.findall('.//gpx:trkpt', ns):
            lat = trkpt.get('lat')
            lon = trkpt.get('lon')
            time_elem = trkpt.find('gpx:time', ns)
            if time_elem is not None:
                time_str = time_elem.text
                dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")
                date = dt.strftime("%Y/%m/%d")
                time = dt.strftime("%H:%M:%S")
                writer.writerow([lat, lon, date, time])

def process_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".gpx"):
            gpx_file = os.path.join(directory, filename)
            csv_file = os.path.join(directory, filename[:-4] + ".csv")
            gpx_to_csv(gpx_file, csv_file)
            print(f"Converted {filename} to CSV")

# 사용 예:
directory = "E:/OneDrive/ALTIBASE/aws/runkeeper"  # GPX 파일이 있는 디렉토리 경로로 변경하세요
process_directory(directory)