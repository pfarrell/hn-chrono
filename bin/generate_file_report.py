import paramiko
from datetime import datetime
import os

def remote_file_info(hostname, port, username, dir):
    # Establish an SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect using the SSH agent
    client.connect(hostname, port=port, username=username, allow_agent=True)

    # Command to navigate to the directory and list directories
    stdin, stdout, stderr = client.exec_command(f"find {dir} -type d -name '20*'")  # Adjust path as needed
    directories = stdout.read().decode().split()
    
    file_info_list = []

    for directory in directories:
        # Command to list all gzipped files in the directory
        print(directory)
        stdin, stdout, stderr = client.exec_command(f"cd {directory} && ls *.gz")
        files = stdout.read().decode().split()
        
        for file in files:
            full_path = f"{directory}/{file}"
            # Get file metadata
            stdin, stdout, stderr = client.exec_command(f"stat --format='%Y %s' {full_path}")
            last_modified_date, size = stdout.read().decode().strip().split()

            # Parse and format the date
            # Convert from "2024-04-01 13:01:54.123456789 -0400" to "Apr 1 2024 13:01"
            last_modified_date = datetime.utcfromtimestamp(int(last_modified_date)).strftime('%b %d %Y %H:%M')

            # Get MD5 hash of the gzipped file
            stdin, stdout, stderr = client.exec_command(f"md5sum {full_path}")
            md5_hash = stdout.read().decode().split()[0]

            # Count lines without unzipping
            stdin, stdout, stderr = client.exec_command(f"zcat {full_path} | wc -l")
            line_count = stdout.read().decode().strip()

            file_info = {
                'path': directory[17:],
                'filename': file,
                'last_modified_date': last_modified_date,
                'size_bytes': size,
                'line_count': line_count,
                'md5_hash': md5_hash
            }
            file_info_list.append(file_info)

    client.close()
    return file_info_list

def write_html(file_data, output_path='fileinfo.html'):
    # Start of the HTML document
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>File Information</title>
        <style>
            body {
                font-family: arial;
            }
            h1 {
                text-align: center;
            }
            p {
                max-width: 50%;
            }
            table {
                border-collapse: collapse;
            }
            th, td {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }
            th {
                background-color: #f2f2f2;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .center {
                margin-left: auto;
                margin-right: auto;
            }
        </style>
    </head>
    <body>
        <h1>Hacker News Data Files</h1>
        <p class="center">This a data dump of content from <a href="https://news.ycombinator.com">Hacker News</a>. See <a href="https://github.com/pfarrell/hn-chrono">this project</a> for more information on how the data was obtained.</p>
        <p class="center">
            Files are gzipped csv files with a header in each file.  Rows in the csv are refer to "items".  Hacker News uses (or at least publishes) their data using <a href="https://en.wikipedia.org/wiki/Single_Table_Inheritance">single table inheritance</a> as ids are unique across different item types (e.g. comments and stories) and arbitraty parent-child relationships between stories or comments and comments use those ids. 
        </p>
        <p>
            <table class="center">
            <tr>
                <th>name</th>
                <th>data type</th>
                <th>notes</th>
            </tr>    
            <tr>
                <td>id</td>
                <td>integer </td>
                <td>unique id for the item</td>
            </tr>
            <tr>
                <td>type</td>
                <td>type of item</td>
                <td>type of item, values include  story, comment, job, poll, pollopt</td>
            </tr>
            <tr>
                <td>score</td>
                <td>integer</td>
                <td>points for a story (comment points are not publicly available)</td>
            </tr>
            <tr>
                <td>by</td>
                <td>string</td>
                <td>username of author</td>
            </tr>
            <tr>
                <td>title</td>
                <td>string</td>
                <td>title of submission, null if type is not story</td>
            </tr>
            <tr>
                <td>url</td>
                <td>string</td>
                <td>link for stories, null if type is not story</td>
            </tr>
            <tr>
                <td>text</td>
                <td>string</td>
                <td>comment text, generally null if type is story</td>
            </tr>
            <tr>
                <td>time</td>
                <td>int</td>
                <td>unix epoch time of publishing</td>
            </tr>
            <tr>
                <td>parent</td>
                <td>int</td>
                <td>parent item.  Null if type is story</td>
            </tr>
            <tr>
                <td>descendants</td>
                <td>int</td>
                <td>number of item children</td>
            </tr>
            <tr>
                <td>dead</td>
                <td>boolean</td>
                <td>1 means comment was flagged and marked dead</td>
            </tr>
            <tr>
                <td>deleted</td>
                <td>boolean</td>
                <td>1 means item was deleted</td>
            </tr> 
        </table>
        </p>
        
        <table class="center">
            <tr>
                <th>Filename</th>
                <th>MD5 Hash</th>
                <th>Size (bytes)</th>
                <th>Line Count</th>
                <th>Last Modified Date (UTC)</th>
            </tr>
    '''

    # Add rows for each file
    file_data.reverse()
    for file_info in file_data:
        html_content += f'''
            <tr>
                <td><a href="https://patf.com/hn-data/{file_info['path']}/{file_info['filename']}">{file_info['filename']}</a></td>
                <td>{file_info['md5_hash']}</td>
                <td>{file_info['size_bytes']}</td>
                <td>{file_info['line_count']}</td>
                <td>{file_info['last_modified_date']}</td>
            </tr>
        '''

    # Closing tags for HTML
    html_content += '''
        </table>
    </body>
    </html>
    '''

    # Write HTML content to a file
    with open(output_path, 'w') as f:
        f.write(html_content)
    print(f"HTML file created: {output_path}")

if __name__ == '__main__':
    hostname = '172.16.1.15'
    port = 22  # Default SSH port, adjust if different
    username = 'pfarrell'
    info = remote_file_info(hostname, port, username, '/volume1/hn-data/')
    write_html(info)
