from Gaudi.Configuration import *

#
#  from $FCCSWBASEDIR/share/FCCSW/Examples//options/geant_fullsim_fccee_hepevt.py
#

# To run it :
# fccrun.py geant_fullsim_fccee_hepevt_CLD.py --input=input.hepevt --outputfile=pairs_fccsw_CLD.root
#
# An example input file (one Guinea-Pig event) can be found in afs in
# /afs/cern.ch/user/e/eperez/public/FCCee/input_example_GuineaPig.hepevt
#


# Data service
from Configurables import FCCDataSvc
podioevent = FCCDataSvc("EventDataSvc")

from Configurables import GaussSmearVertex
from GaudiKernel import SystemOfUnits as units
smeartool = GaussSmearVertex()
smeartool.xVertexSigma =   0.5*units.mm
smeartool.yVertexSigma =   0.5*units.mm
smeartool.zVertexSigma =  40.0*units.mm
smeartool.tVertexSigma = 180.0*units.picosecond

from Configurables import PythiaInterface
pythia8gentool = PythiaInterface()
pythia8gentool.Filename = "k4Gen/k4Gen/data/ee_Z_ddbar.cmd" 
pythia8gentool.doEvtGenDecays = False
pythia8gentool.printPythiaStatistics = True

from Configurables import GenAlg
pythia8gen = GenAlg("Pythia8")
pythia8gen.SignalProvider = pythia8gentool
pythia8gen.VertexSmearingTool = smeartool
pythia8gen.hepmc.Path = "hepmc"
pythia8gen.OutputLevel = DEBUG

### Reads an HepMC::GenEvent from the data service and writes a collection of EDM Particles
from Configurables import HepMCToEDMConverter
hepmc_converter = HepMCToEDMConverter()
hepmc_converter.hepmc.Path="hepmc"
hepmc_converter.hepmcStatusList = [1] # convert particles with all statuses
hepmc_converter.genparticles.Path="GenParticles"
hepmc_converter.genvertices.Path="GenVertices"


# DD4hep geometry service
# Parses the given xml file
from Configurables import GeoSvc, SimG4SingleParticleGeneratorTool
geoservice = GeoSvc("GeoSvc", detectors=['FCCDetectors/Detector/DetFCCeeCLD/compact/FCCee_DectMaster.xml'])
geoservice.OutputLevel = INFO

from Configurables import SimG4ConstantMagneticFieldTool
field = SimG4ConstantMagneticFieldTool("SimG4ConstantMagneticFieldTool", FieldOn=True, FieldComponentZ=0.002, IntegratorStepper="ClassicalRK4")


# Geant4 service
# Configures the Geant simulation: geometry, physics list and user actions
from Configurables import SimG4Svc, SimG4FullSimActions, SimG4UserLimitPhysicsList, SimG4UserLimitRegion
from GaudiKernel.SystemOfUnits import mm

regiontool = SimG4UserLimitRegion("limits", volumeNames=["world"],
                                  maxStep = 2*mm)

physicslisttool = SimG4UserLimitPhysicsList("Physics", fullphysics="SimG4FtfpBert")

actions = SimG4FullSimActions()
actions.enableHistory=True
# giving the names of tools will initialize the tools of that type
geantservice = SimG4Svc("SimG4Svc", detector='SimG4DD4hepDetector', physicslist=physicslisttool, 
                        actions=actions, 
                        regions=[regiontool],
                        magneticField=field,
			g4PostInitCommands=['/random/setSeeds 1234500 3456700']
                        )

#geantservice.g4PostInitCommands += ["/run/setCut 0.7 mm"]
#geantservice.g4PostInitCommands +=["/process/eLoss/minKinEnergy 1 MeV"]
#geantservice.g4PostInitCommands +=["/score/quantity/energyDeposit edep1kev"]
geantservice.g4PostInitCommands += ["/tracking/storeTrajectory 1"]


# Geant4 algorithm
# Translates EDM to G4Event, passes the event to G4, writes out outputs via tools
from Configurables import SimG4Alg, SimG4SaveTrackerHits, SimG4SaveCalHits, SimG4PrimariesFromEdmTool, SimG4SaveParticleHistory, SimG4SaveTrajectory
# first, create a tool that saves the tracker hits
# Name of that tool in GAUDI is "XX/YY" where XX is the tool class name ("SimG4SaveTrackerHits")
# and YY is the given name ("saveTrackerHits")


savetrajectorytool = SimG4SaveTrajectory("saveTrajectory")
savetrajectorytool.trajectory.Path = "trajectory"
savetrajectorytool.trajectoryPoints.Path = "trajectoryPoints"


savehisttool = SimG4SaveParticleHistory("saveHistory")
savehisttool.mcParticles.Path = "simParticles"
savehisttool.genVertices.Path = "simVertices"


savetrackertool = SimG4SaveTrackerHits("saveTrackerHits_Barrel", readoutNames = ["VertexBarrelCollection"])
savetrackertool.positionedTrackHits.Path = "positionedHits_VXD_barrel"
savetrackertool.trackHits.Path = "hits_VXD_barrel"
savetrackertool.digiTrackHits.Path = "digiHits_VXD_barrel"

savetrackertool_endcap = SimG4SaveTrackerHits("saveTrackerHits_Endcap", readoutNames = ["VertexEndcapCollection"])
savetrackertool_endcap.positionedTrackHits.Path = "positionedHits_VXD_endcap"
savetrackertool_endcap.trackHits.Path = "hits_VXD_endcap"
savetrackertool_endcap.digiTrackHits.Path = "digiHits_VXD_endcap"

savetrackertool_ITB = SimG4SaveTrackerHits("saveTrackerHits_IT_Barrel", readoutNames = ["InnerTrackerBarrelCollection"])
savetrackertool_ITB.positionedTrackHits.Path = "positionedHits_IT_barrel"
savetrackertool_ITB.trackHits.Path = "hits_IT_barrel"
savetrackertool_ITB.digiTrackHits.Path = "digiHits_IT_barrel"

savetrackertool_ITE = SimG4SaveTrackerHits("saveTrackerHits_IT_Endcap", readoutNames = ["InnerTrackerEndcapCollection"])
savetrackertool_ITE.positionedTrackHits.Path = "positionedHits_IT_endcap"
savetrackertool_ITE.trackHits.Path = "hits_IT_endcap"
savetrackertool_ITE.digiTrackHits.Path = "digiHits_IT_endcap"

savetrackertool_OTB = SimG4SaveTrackerHits("saveTrackerHits_OT_Barrel", readoutNames = ["OuterTrackerBarrelCollection"])
savetrackertool_OTB.positionedTrackHits.Path = "positionedHits_OT_barrel"
savetrackertool_OTB.trackHits.Path = "hits_OT_barrel"
savetrackertool_OTB.digiTrackHits.Path = "digiHits_OT_barrel"

savetrackertool_OTE = SimG4SaveTrackerHits("saveTrackerHits_OT_Endcap", readoutNames = ["OuterTrackerEndcapCollection"])
savetrackertool_OTE.positionedTrackHits.Path = "positionedHits_OT_endcap"
savetrackertool_OTE.trackHits.Path = "hits_OT_endcap"
savetrackertool_OTE.digiTrackHits.Path = "digiHits_OT_endcap"

savelumicaltool = SimG4SaveCalHits("saveLumicalHits", readoutNames = ["LumiCalCollection"])
savelumicaltool.positionedCaloHits.Path = "positionedHits_Lumical"
savelumicaltool.caloHits.Path = "hits_Lumical"

saveEcalBarreltool = SimG4SaveCalHits("saveEcalBarrelHits", readoutNames = ["ECalBarrelCollection"])
saveEcalBarreltool.positionedCaloHits.Path = "positionedHits_EcalBarrel"
saveEcalBarreltool.caloHits.Path = "hits_EcalBarrel"

saveEcalEndcaptool = SimG4SaveCalHits("saveEcalEndcapHits", readoutNames = ["ECalEndcapCollection"])
saveEcalEndcaptool.positionedCaloHits.Path = "positionedHits_EcalEndcap"
saveEcalEndcaptool.caloHits.Path = "hits_EcalEndcap"

saveHcalBarreltool = SimG4SaveCalHits("saveHcalBarrelHits", readoutNames = ["HCalBarrelCollection"])
saveHcalBarreltool.positionedCaloHits.Path = "positionedHits_HcalBarrel"
saveHcalBarreltool.caloHits.Path = "hits_HcalBarrel"

saveHcalEndcaptool = SimG4SaveCalHits("saveHcalEndcapHits", readoutNames = ["HCalEndcapCollection"])
saveHcalEndcaptool.positionedCaloHits.Path = "positionedHits_HcalEndcap"
saveHcalEndcaptool.caloHits.Path = "hits_HcalEndcap"

#from Configurables import SimG4SingleParticleGeneratorTool
#pgun = SimG4SingleParticleGeneratorTool("GeantinoGun")
#pgun.etaMin=0
#pgun.etaMax=2.5
#pgun.phiMin=0
#pgun.phiMax=360
#pgun.energyMin=0
#pgun.energyMax=10
#pgun.particleName="pi-"

## next, create the G4 algorithm, giving the list of names of tools ("XX/YY")
particle_converter = SimG4PrimariesFromEdmTool("EdmConverter")
particle_converter.genParticles.Path = "GenParticles"
particle_converter.OutputLevel = DEBUG

geantsim = SimG4Alg("SimG4Alg",
                    outputs= [
        "SimG4SaveTrajectory/saveTrajectory",
        "SimG4SaveParticleHistory/saveHistory",
        "SimG4SaveTrackerHits/saveTrackerHits_Barrel", 
        "SimG4SaveTrackerHits/saveTrackerHits_Endcap",
        "SimG4SaveTrackerHits/saveTrackerHits_IT_Barrel",
        "SimG4SaveTrackerHits/saveTrackerHits_IT_Endcap",
        "SimG4SaveTrackerHits/saveTrackerHits_OT_Barrel",
        "SimG4SaveTrackerHits/saveTrackerHits_OT_Endcap",
	"SimG4SaveCalHits/saveLumicalHits",
  	"SimG4SaveCalHits/saveEcalBarrelHits",
	"SimG4SaveCalHits/saveEcalEndcapHits",
        "SimG4SaveCalHits/saveHcalBarrelHits",
        "SimG4SaveCalHits/saveHcalEndcapHits"
        ],
    eventProvider=particle_converter
)


# PODIO algorithm
from Configurables import PodioOutput
out = PodioOutput("out",
                  filename="out.root",
                  OutputLevel=DEBUG)
out.outputCommands = ["keep *"]

# ApplicationMgr
from Configurables import ApplicationMgr
ApplicationMgr( TopAlg = [pythia8gen, hepmc_converter, geantsim, out],
                EvtSel = 'NONE',
                EvtMax   = 10,
                # order is important, as GeoSvc is needed by SimG4Svc
                ExtSvc = [podioevent, geoservice, geantservice],
                OutputLevel=DEBUG
                )
