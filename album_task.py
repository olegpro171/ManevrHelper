import os

from XF import XenonFile

task_pattern = """
Unit = {xe_directory_absolute_no_K07}
Graph = {graph_dir}

RC_Axs_Sost {camp_name} [{name} (Bar = (0,280,243,280,375,240), Process=Total, 2Dpole=none, Sfactor=yes, Type=File, NumSost=({state}-{count}))

RC2_5 {camp_name} [{name} (Type=File, BaseSost=1,  Interval = 0.1, PSI_Interval = 5.0, NumSost=({state}-{count}),
& Process = Total, SFactor=yes, Cancel = BarLine, Bar = ( 
&  22.0, 160,
&  24.0, 160.0,
&  28.0, 90.0,
&  30.0, 85.0,
&  40.0, 77.0,
&  70.0, 75.0,
& ) )

RC2_5 {camp_name} [{name} (Type=File, BaseSost=2,  Interval = 0.1, PSI_Interval = 5.0, NumSost=({state}-{count}),  
& Process = Total, SFactor=yes, Cancel = BarLine, Bar = ( 
&  22.0, 160,
&  24.0, 160.0,
&  28.0, 90.0,
&  30.0, 85.0,
&  40.0, 77.0,
&  70.0, 75.0,
& ) )

Binary = {xe_directory_absolute}

Permak_Sost_Tabl {name}, 
{count_format}
& (Graph  = None, Type=File)

end
"""

class AlbumTask:
    def get_task_text(file: XenonFile, count: int, state: int, new_dir: str, camp_name):
        xe_directory_absolute: str = os.path.abspath(file.DirEntry.path)

        base_name = file.DirEntry.name.split('.')[0]
        return task_pattern.format(
            name = base_name,
            state = state, 
            count = count, 
            count_format = AlbumTask._generate_count_format(count, base_name),
            xe_directory_absolute = xe_directory_absolute[:-9],
            xe_directory_absolute_no_K07 = xe_directory_absolute[:-13],
            graph_dir=new_dir,
            camp_name=camp_name,
        )
    

    def _generate_count_format(end_index: int, base_name: str) -> str:
        lines = []
        step = 100
        
        # Generate the ranges in increments of 100
        for start in range(0, end_index + 1, step):
            if start == 0:
                start = 1
            end = min(start + step - 1, end_index)
            if (end == step):
                end = step - 1
            # Format each line with the ranges
            line = f"{base_name}.S{start:02d} - {base_name}.S{end:02d}"
            lines.append(line)
        
        # Combine lines, ensuring the first line starts with '&'
        result = ",\n& ".join(lines) + ', '
        
        # Add the initial '& ' for the first line
        result = "& " + result

        return result
