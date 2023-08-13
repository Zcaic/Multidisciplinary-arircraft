import copy
from aerosandbox import numpy as np
import aerosandbox as asb

from typing import List

class Asb2Cad:
    def __init__(self, airplane: asb.Airplane) -> None:
        self.airplane = airplane
        self.wings = self.airplane.wings
        self.fuselages = self.airplane.fuselages

    def export_cadquery_geometry(
        self, filename: str, minimum_airfoil_TE_thickness: float = 0.001,union=False
    ) -> None:
        """
        Exports the airplane geometry to a STEP file.

        Args:
            filename: The filename to export to. Should include the ".step" extension.

            minimum_airfoil_TE_thickness: The minimum thickness of the trailing edge of the airfoils, as a fraction
            of each airfoil's chord. This will be enforced by thickening the trailing edge of the airfoils if
            necessary. This is useful for avoiding numerical issues in CAD software that can arise from extremely
            thin (i.e., <1e-6 meters) trailing edges.

        Returns: None, but exports the airplane geometry to a STEP file.
        """
        solid = self.generate_cadquery_geometry(
            minimum_airfoil_TE_thickness=minimum_airfoil_TE_thickness,
        )

        solid.objects = [o.scale(1000) for o in solid.objects]
        if union:
            solid=solid.combine()

        from cadquery import exporters

        exporters.export(solid, fname=filename)

    def generate_cadquery_geometry(
        self,
        minimum_airfoil_TE_thickness: float = 0.001,
        fuselage_tol: float = 1e-4,
    ):
        """
        Uses the CADQuery library (OpenCASCADE backend) to generate a 3D CAD model of the airplane.

        Args:

            minimum_airfoil_TE_thickness: The minimum thickness of the trailing edge of the airfoils, as a fraction
            of each airfoil's chord. This will be enforced by thickening the trailing edge of the airfoils if
            necessary. This is useful for avoiding numerical issues in CAD software that can arise from extremely
            thin (i.e., <1e-6 meters) trailing edges.

            tol: The geometric tolerance (meters) to use when generating the CAD geometry. This is passed directly to the CADQuery

        Returns: A CADQuery Workplane object containing the CAD geometry of the airplane.

        """
        import cadquery as cq

        solids = []

        for wing in self.wings:
            xsec_wires:list[cq.Workplane] = []

            for i, xsec in enumerate(wing.xsecs):
                csys = wing._compute_frame_of_WingXSec(i)

                af = xsec.airfoil
                if af.TE_thickness() < minimum_airfoil_TE_thickness:
                    af = af.set_TE_thickness(thickness=minimum_airfoil_TE_thickness)
                
                leindex = af.LE_index()
                wp = cq.Workplane(
                    inPlane=cq.Plane(
                        origin=tuple(xsec.xyz_le),
                        xDir=tuple(csys[0]),
                        normal=tuple(-csys[1]),
                    )
                )

                upperspline = wp.spline(
                    listOfXYTuple=[
                        tuple(xy * xsec.chord) for xy in af.coordinates[: leindex + 1]
                    ]
                ).spline(
                    listOfXYTuple=[
                        tuple(xy * xsec.chord) for xy in af.coordinates[leindex:]
                    ]
                ).close()

                xsec_wires.append(upperspline)
                # xsec_wires.append(
                #     cq.Workplane(
                #         inPlane=cq.Plane(
                #             origin=tuple(xsec.xyz_le),
                #             xDir=tuple(csys[0]),
                #             normal=tuple(-csys[1]),
                #         )
                #     )
                #     .spline(
                #         listOfXYTuple=[tuple(xy * xsec.chord) for xy in af.coordinates]
                #     )
                #     .close()
                # )

            wire_collection = xsec_wires[0]
            for s in xsec_wires[1:]:
                wire_collection.ctx.pendingWires.extend(s.ctx.pendingWires)

            loft = wire_collection.loft(ruled=True, clean=False)

            solids.append(loft)

            if wing.symmetric:
                loft = loft.mirror(mirrorPlane="XZ", union=False)

                solids.append(loft)

        for fuse in self.fuselages:
            xsec_wires = []

            for i, xsec in enumerate(fuse.xsecs):
                if (
                    xsec.height < fuselage_tol or xsec.width < fuselage_tol
                ):  # If the xsec is so small as to effectively be a point
                    xsec = copy.deepcopy(
                        xsec
                    )  # Modify the xsec to be big enough to not error out.
                    xsec.height = np.maximum(xsec.height, fuselage_tol)
                    xsec.width = np.maximum(xsec.width, fuselage_tol)

                xsec_wires.append(
                    cq.Workplane(
                        inPlane=cq.Plane(
                            origin=tuple(xsec.xyz_c), xDir=(0, 1, 0), normal=(-1, 0, 0)
                        )
                    )
                    .spline(
                        listOfXYTuple=[
                            (y - xsec.xyz_c[1], z - xsec.xyz_c[2])
                            for x, y, z in zip(
                                *xsec.get_3D_coordinates(
                                    theta=np.linspace(
                                        np.pi / 2, np.pi / 2 + 2 * np.pi, 181
                                    )
                                )
                            )
                        ]
                    )
                    .close()
                )

            wire_collection = xsec_wires[0]
            for s in xsec_wires[1:]:
                wire_collection.ctx.pendingWires.extend(s.ctx.pendingWires)

            loft = wire_collection.loft(ruled=True, clean=False)

            solids.append(loft)

        solid:cq.Workplane = solids[0]
        for s in solids[1:]:
            solid.add(s)

        return solid.clean()


def af2geometry(af:asb.Airfoil,filename:str,scale:float=1000):
    import cadquery as cq

    # leindex=af.LE_index()
    wq=cq.Workplane(
        "XY"
    ).spline(
        listOfXYTuple=[
            tuple(xy*scale) for xy in af.upper_coordinates()
        ]
    ).spline(
        listOfXYTuple=[
            tuple(xy*scale) for xy in af.lower_coordinates()
        ]
    ).close()
    cq.exporters.export(wq,fname=filename)

def af2VSP(af:asb.Airfoil,filename:str):
    uc=af.upper_coordinates()
    lc=af.lower_coordinates()
    with open(filename,'w') as fin:
        print(af.name,file=fin)
        print(f'{uc.shape[0]} {lc.shape[0]}\n',file=fin)
        np.savetxt(fin,uc[::-1],delimiter=' ')
        fin.write('\n')
        np.savetxt(fin,lc,delimiter=' ')

def af2XYZ(af:asb.Airfoil,filename:str):
    uc=af.upper_coordinates()
    lc=af.lower_coordinates()
    with open(filename,'w') as fin:
        print(lc.shape[0],file=fin)
        np.savetxt(fin,lc,delimiter=' ')
        print(uc.shape[0],file=fin)
        np.savetxt(fin,uc[::-1],delimiter=' ')  


