"""Ejecuta todas las celdas reales en un proceso nuevo y guarda sus salidas."""
from pathlib import Path
import os
import traceback
import nbformat
from IPython.terminal.interactiveshell import TerminalInteractiveShell
from IPython.utils.capture import capture_output
from matplotlib_inline.backend_inline import flush_figures

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'notebooks/Avance4.Equipo4.ipynb'
os.chdir(path.parent)
notebook=nbformat.read(path,as_version=4)
shell=TerminalInteractiveShell.instance()
shell.run_line_magic('matplotlib','inline')
shell.display_formatter.active_types=['text/plain','text/html','text/markdown','image/png','image/svg+xml']
for formatter in shell.display_formatter.formatters.values():
    formatter.enabled=True
count=0
for cell in notebook.cells:
    if cell.cell_type!='code':
        continue
    count+=1
    print(f'Inicia celda {count}',flush=True)
    cell.outputs=[]
    cell.execution_count=count
    with capture_output(display=True) as captured:
        result=shell.run_cell(cell.source,store_history=False)
        flush_figures()
    if captured.stdout:
        cell.outputs.append(nbformat.v4.new_output('stream',name='stdout',text=captured.stdout))
    if captured.stderr:
        cell.outputs.append(nbformat.v4.new_output('stream',name='stderr',text=captured.stderr))
    for output in captured.outputs:
        cell.outputs.append(nbformat.v4.new_output('display_data',data=output.data,metadata=output.metadata))
    error=result.error_before_exec or result.error_in_exec
    print(f'Celda {count}: '+('ERROR' if error else 'OK'),flush=True)
    if error:
        cell.outputs.append(nbformat.v4.new_output('error',ename=type(error).__name__,evalue=str(error),
                                                   traceback=traceback.format_exception(error)))
        nbformat.write(notebook,path)
        raise error
notebook.metadata['ejecucion']={
    'metodo':'IPython en proceso nuevo; celdas reales ejecutadas secuencialmente, namespace limpio, sin sockets de kernel',
    'celdas_codigo':count,'errores':0}
nbformat.validate(notebook)
nbformat.write(notebook,path)
print(f'Ejecución completa: {count} celdas, sin errores.')
