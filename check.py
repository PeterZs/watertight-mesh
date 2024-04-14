from pathlib import Path
import shutil
import trimesh
import pymeshfix


def check_watertight():
    dat_dir = Path(__file__).parent / 'data'
    for mesh_dir in sorted(dat_dir.iterdir(), key=lambda x: x.name.casefold()):
        if not mesh_dir.is_dir():
            continue
        for mesh_file in sorted(mesh_dir.glob('*.ply'), key=lambda x: x.name.casefold()):
            if not mesh_file.is_file():
                continue
            mesh = trimesh.load_mesh(str(mesh_file))
            is_watertight = mesh.is_watertight
            if not is_watertight:
                print(f'Mesh {mesh_file.relative_to(dat_dir)} is not watertight')
                mesh = pymeshfix.MeshFix(mesh.vertices, mesh.faces)
                mesh.repair(verbose=False)
                mesh = trimesh.Trimesh(vertices=mesh.v, faces=mesh.f)
                is_watertight = mesh.is_watertight
                if not is_watertight:
                    raise RuntimeError(f'Mesh {mesh_file.relative_to(dat_dir)} is still not watertight')
            num_vertices = round(len(mesh.vertices) / 1000)
            num_faces = round(len(mesh.triangles) / 1000)
            print(f'Mesh {mesh_file.relative_to(dat_dir)}, watertight: {is_watertight}, #vertices: {num_vertices}k, #faces: {num_faces}k')
            old_vertices = mesh.vertices.copy()
            mesh.vertices -= mesh.bounds[0]
            mesh.vertices /= mesh.extents.max()
            mesh.vertices -= mesh.bounds.mean(axis=0)
            if (old_vertices == mesh.vertices).all():
                continue
            print(f'Mesh {mesh_file.relative_to(dat_dir)} has been normalized')
            mesh.export(str(mesh_file), file_type='ply')

if __name__ == '__main__':
    check_watertight()
