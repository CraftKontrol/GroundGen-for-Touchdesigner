"""      
GroundGenExt Module
Author: Arnaud Cassone

"""

from datetime import datetime
from TDStoreTools import StorageManager
import TDFunctions as TDF
import json
import os
import CraftGGenUtils as CraftGGenUtils
import datetime
class GroundGenExt:
	"""
	GroundGenExt is an extension for the GGen node.
	This extension manages ground generation and terrain splatmapping functionality.
	It handles dynamic shader generation, texture management, and material property
	configuration for multi-layered terrain rendering.

	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp

		# properties
		TDF.createProperty(self, 'Installed', value=False, dependable=True,readOnly=False)
		TDF.createProperty(self, 'Splats', value=[], dependable=True,readOnly=False)
		TDF.createProperty(self, 'Licence', value="", dependable=True,readOnly=False)

		
		if hasattr(op, 'SplatmapsNetwork'):
			op.SplatmapsNetwork.op('Startup').par.startpulse.pulse()

		if hasattr(op, 'TerrainNetwork'):
			op.TerrainNetwork.op('Startup').par.startpulse.pulse()



	def Startup(self):
		print("GGen Started")
		self.RestartAllCustomNodes()
		# public mit licence
		self.Licence = '''Copyright (c) 2025 Arnaud Cassone, Artcraft Visuals

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. 	

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE  FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 

'''	
		op.GGenLogger.Info("Initializing GroundGenExt") 
		if self.Setup():

			self.Installed = True

		else:
			op.GGenLogger.Error('GroundGenExt Setup failed')
			self.Installed = False
			return
		if hasattr(op, 'SplatmapsNetwork'):
			if self.Installed:
				self.UpdateSplats()
		
		self.SetShaderParams()


		op.GGenLogger.Info("Shader Compiled")
		return
	
	def Setup(self):
		op.GGenLogger.Info('GroundGenExt Setup')

		# Create the default config file
		default = {
			"Touchdesigner version": app.version + " " + app.build,
			"GGen version": str(parent().par.Header.label).split('Version ')[1],
			"Last Updated": "",
			"settings": {
				"TerrainNetwork": "", 
				"SplatmapsNetwork": "", 
			
			},
			"Splatmaps": {
				"op": "",
				"inputs": {},
				"outputs": {}
			},
			"Terrain": {
				"op": "",
				"inputs": {},
				"outputs": {}
			},
			"Shader": {
				"Param": {},
				"Value": {}
			}
		}
		# setup the config files
		# check if config.json in user/GGen exists, if not copy it from the default config
		try:
			configPath = parent().par.Ggenfolder + '/config.json'
			op.GGenLogger.Info('Config path: ' + configPath)
			if not os.path.exists(configPath):
				op.GGenLogger.Info('Creating default config file')
				# create the directory if it does not exist
				os.makedirs(os.path.dirname(configPath), exist_ok=True)
				# write the default config to the file
				with open(configPath, 'w') as f:
					json.dump(default, f, indent=4)
				 
			else:
				op.GGenLogger.Info('Config file already exists, skipping creation')		
			
			return True
		except Exception as e:
			op.GGenLogger.Error('Error creating config file: ' + str(e))
			return False
	def RestartAllCustomNodes(self):
		op.GGenLogger.Info('Restarting all custom nodes')
		for node in op.GGen.op('custom_operators').findChildren(tags=['GGen2d','GGen3d','GGenOut'], depth=1):
			#print('Restarting node: ' + str(node))
			if node.op('Startup') is not None:
				node.op('Startup').par.startpulse.pulse()

	def OnSave(self):
		op.GGenLogger.Info('Saving GroundGenExt state')
		splatNet = ""
		geoNet = ""
		splats = []
		geos = []
		if hasattr(op, 'SplatmapsNetwork'):
			splatNet = str(op.SplatmapsNetwork)
			
			# Find all splat maps in the SplatmapsNetwork
			for node in op.SplatmapsNetwork.findChildren(tags=['GGen2d','GGen3d', 'Splatmap']):
				source = []
				dest = []
				for par in node.pars():
					if "Source" in par.name:
						source.append((par.name, par.eval()))
					if "Paramname" in par.name:
						dest.append((par.name, par.eval()))
				info = {
					"op": str(node),
					"inputs": source,
					"outputs": dest
				}
				splats.append(info)
		
		if hasattr(op, 'TerrainNetwork'):
			geoNet = str(op.TerrainNetwork)	

			for node in op.TerrainNetwork.findChildren(tags=['GGen2d','GGen3d']):
				source = []
				dest = []
				for par in node.pars():
					if "Source" in par.name:
						source.append((par.name, par.eval()))
					if "Paramname" in par.name:
						dest.append((par.name, par.eval()))
				info = {
					"op": str(node),
					"inputs": source,
					"outputs": dest
				}
				geos.append(info)

		version = str(parent().par.Header.label).split('Version ')[1]

		shader = []

		for i in range(op.ShaderGGen.op('parameter1').numRows):
			param = {
				"name": str(op.ShaderGGen.op('parameter1')[i, 0]),
				"value": str(op.ShaderGGen.op('parameter1')[i, 1])
			}
			shader.append(param)
		
			#print(version)
		configPath = parent().par.Ggenfolder + '/config.json'
		# read write
		with open(configPath, 'r+') as f:
			config = json.load(f)
			
			config['Last Updated'] = str(datetime.datetime.now())
			config['settings']['SplatmapsNetwork'] = splatNet
			config['settings']['TerrainNetwork'] = geoNet
			config['Splatmaps'] = splats
			config['Terrain'] = geos
			config['GGen version'] = version
			config['Shader'] = shader
			f.seek(0)
			json.dump(config, f, indent=4)

	def Update(self):
		# compare the splat maps in the SplatmapsNetwork with the current splats
		# if the splat maps have changed, update the splats

		# remove Base layer if present
		for splat in self.Splats:
			
			if "/GGen/Shader" in str(splat):
				# delete it
				self.Splats.remove(splat)	
		if not hasattr(op, 'SplatmapsNetwork'):
			return

		if  op.SplatmapsNetwork.op('UserNetwork').findChildren(tags=['Splatmap']) != self.Splats:
			op.GGenLogger.Info('Splat maps changed')
			self.UpdateSplats()
		pass

	def UpdateSplats(self):

		op.GGenLogger.Info('Start updating splat maps') 

	

	
		# Find all splat maps in the SplatmapsNetwork
		self.Splats = self.FindSplats()


		op.GGenLogger.Info('Found ' + str(len(self.Splats)) + ' splat maps')
		
		if len(self.Splats) == 0:
			
			self.DefaultShader()
			return
		
		op.GGenLogger.Info('Setting multi splat shader')
 
		#add a base layer
		newItem = {'name': 'Base' ,'node': op.GGen.op('Shader/splatMap/out1')}
		op.SplatmapsNetwork.SplatList.append(newItem)
		self.Splats.insert(0, op.GGen.op('Shader/splatMap'))
		#print(self.Splats)

		# Get the ShaderGGen sequence for splatmaps
		seq = op.ShaderGGen.seq.Splatmaps 

		op.GGenLogger.Info('Store sequence parameters')
		# get sequence parameters and store them in a new list 
		seqParams = []
		for i in range(len(seq)):
			# Create a new list for each sequence block
			seqParams.append([])
			for par in seq[i].par:
				# Store the parameter name and value in the list
				seqParams[i].append((par.name.replace("Splatmaps","").replace(str(i),""), par.eval()))



		# Reset the sequence
		seq.numBlocks = 1

		#Set the first splat map header
		op.ShaderGGen.par.Splatmaps0header = 'Base'
		op.ShaderGGen.par.Splatmaps0header.readOnly =  True
		

		# Set the sequence name
		op.GGenLogger.Info('Setup Splatmaps sequence')

		for i in range(len(self.Splats)):
			if i > 0:
				self.AddSplat(seq,self.Splats[i].par.Paramname,i)
				self.SetSplatName(self.Splats[i].par.Paramname, i)

			else:
				self.SetSplatName(self.Splats[i].par.Paramname, i)	 


		# Set the sequence parameters using the stored parameters
		op.GGenLogger.Info('Set Splatmaps stored sequence parameters') 
		for i in range(len(seqParams)):
			for j in range(len(seqParams[i])): 
				# Set the parameter value
				op.ShaderGGen.par['Splatmaps' + str(i) + seqParams[i][j][0]] = seqParams[i][j][1]
				# Set the parameter readOnly state 
				if seqParams[i][j][0] == 'header':
					op.ShaderGGen.par['Splatmaps' + str(i) + seqParams[i][j][0]].readOnly = True
				else:
					op.ShaderGGen.par['Splatmaps' + str(i) + seqParams[i][j][0]].readOnly = False 




		# Generate textures Nodes
		op.GGenLogger.Info('Generate textures Nodes')
		op.ShaderGGen.op('DiffuseReplicator').par.numreplicants = len(self.Splats)
		op.ShaderGGen.op('DiffuseReplicator').par.recreateall.pulse()
		op.ShaderGGen.op('NormalReplicator').par.recreateall.pulse()   
		op.ShaderGGen.op('RoughnessReplicator').par.recreateall.pulse()  




		# Generate Compute Shader  
		self.GenerateComputeShader()
		op.ShaderGGen.op('delayCompute').run(delayFrames=30)


		

		# Add Vertex Shader outputs
		self.SetVertexShaderOutputs()
		
		# Add Fragment Shader inputs
		self.SetPixelShaderInputs()
		
		# Add OutAttributes in vertex shader
		self.SetVertexAttributes()
	
		# Add Attributes in Material
		self.SetMaterialAttributes()
		
		# add Samplers in material
		self.SetMaterialSamplers()
	
		# Linking samplers to parent parameters
		self.BindSamplersToParameters()
		
		# add Samplers to GLSL
		self.SetGLSLSamplers()

		# add Vectors to Material
		self.SetMaterialVectors()
		
		# Set GLSL Uniforms
		self.SetGLSLUniforms()

		# Add defines to GLSL
		self.SetDefines()

		# Add NormalMap Computing
		self.AddNormalMapComputing()
		

		# Add Color Computing
		self.SetColorComputing()

		# Add Roughness Computing
		self.SetRoughnessComputing()

		op.GGenLogger.Info('Splat maps updated successfully') 

		op.ShaderGGen.OnStart()

		return
			

	def DefaultShader(self):
		op.GGenLogger.Info('Setting default shader')
		splat = op('splatMap')
		newItem = {'name': 'Base' ,'node': op.GGen.op('Shader/splatMap/out1')}

		
		op.SplatmapsNetwork.SplatList.append(newItem)

		self.Splats = self.FindSplats()

		# Get the ShaderGGen sequence for splatmaps
		seq = op.ShaderGGen.seq.Splatmaps 

		op.GGenLogger.Info('Store sequence parameters')
		# get sequence parameters and store them in a new list 
		seqParams = []
		for i in range(len(seq)):
			# Create a new list for each sequence block
			seqParams.append([])
			for par in seq[i].par:
				# Store the parameter name and value in the list
				seqParams[i].append((par.name.replace("Splatmaps","").replace(str(i),""), par.eval()))



		# Reset the sequence
		seq.numBlocks = 1

		#Set the first splat map header
		op.ShaderGGen.par.Splatmaps0header = 'Base'
		op.ShaderGGen.par.Splatmaps0header.readOnly =  True


		# Generate textures Nodes
		op.GGenLogger.Info('Generate textures Nodes')
		op.ShaderGGen.op('DiffuseReplicator').par.numreplicants = len(self.Splats)
		op.ShaderGGen.op('DiffuseReplicator').par.recreateall.pulse()
		op.ShaderGGen.op('NormalReplicator').par.recreateall.pulse()   
		op.ShaderGGen.op('RoughnessReplicator').par.recreateall.pulse()  

		# Generate Compute Shader
		self.GenerateComputeShader()

		#Add Generic Splat
		

		# Add Vertex Shader outputs
		self.SetVertexShaderOutputs()

		# Add Fragment Shader inputs
		self.SetPixelShaderInputs()
		
		# Add OutAttributes in vertex shader
		self.SetVertexAttributes()
	
		# Add Attributes in Material
		self.SetMaterialAttributes()
		
		# add Samplers in material
		self.SetMaterialSamplers()
	
		# Linking samplers to parent parameters
		self.BindSamplersToParameters()
		
		# add Samplers to GLSL
		self.SetGLSLSamplers()

		# add Vectors to Material
		self.SetMaterialVectors()
		
		# Set GLSL Uniforms
		self.SetGLSLUniforms()

		# Add defines to GLSL
		self.SetDefines()

		# Add NormalMap Computing
		self.AddNormalMapComputing()
		

		# Add Color Computing
		self.SetColorComputing()

		# Add Roughness Computing
		self.SetRoughnessComputing()

		op.GGenLogger.Info('Splat maps updated successfully') 

		op.ShaderGGen.OnStart()

		pass

	def AddSplat(self, seq, name, index):
		# Add a new block to the sequence 
		
		seq.numBlocks += 1	 
		return   

	def SetSplatName(self, name,index):
		# Set the name of the splat map in the ShaderGGen parameters
		
		op.ShaderGGen.par['Splatmaps' + str(index) + 'header'] = name 
		op.ShaderGGen.par['Splatmaps' + str(index) + 'header'].readOnly = True 
		op.ShaderGGen.par['Splatmaps' + str(index) + 'diffusemap'] = op.ShaderGGen.op('TexturePlaceholder')
		op.ShaderGGen.par['Splatmaps' + str(index) + 'normalmap'] = op.ShaderGGen.op('TexturePlaceholder')
		op.ShaderGGen.par['Splatmaps' + str(index) + 'roughnessmap'] = op.ShaderGGen.op('TexturePlaceholder')
		op.ShaderGGen.par['Splatmaps' + str(index) + 'heightmap'] = op.ShaderGGen.op('TexturePlaceholder')
 
		return
	
	def FindSplats(self):
		# Find all splat maps in the TerrainNetwork
		return op.SplatmapsNetwork.op('UserNetwork').findChildren(tags=['Splatmap'])
	 

	def GenerateComputeShader(self):
		# Generate the compute shader for splat maps
		op.GGenLogger.Info('Generate Compute Shader')
		computeIn = op.ShaderGGen.op('GlslCompute').text

		# Handle case with no splat maps
		if len(self.Splats) == 0:
			op.ShaderGGen.op('GLSL3DTextureRefiller').par.customdepth = 1
			out = "" 
			out += "vec4 input" + str(0) +  " = texelFetch(sTD2DInputs[" + str(0) +  "], ivec2(gl_GlobalInvocationID.xy), 0);\n"
			out += "imageStore(mTDComputeOutputs[0], ivec3(gl_GlobalInvocationID.xy," + str(0) +  "), TDOutputSwizzle(" + "input" + str(0) +  "));\n"
			op.ShaderGGen.op('FinalGLslCompute').text = computeIn.replace("PLACEHOLDER_COMPUTE", out)

			return

		# normal case
		op.ShaderGGen.op('GLSL3DTextureRefiller').par.customdepth = len(self.Splats)
		out = "" 
		for i in range(len(self.Splats)):
			out += "vec4 input" + str(i) +  " = texelFetch(sTD2DInputs[" + str(i) +  "], ivec2(gl_GlobalInvocationID.xy), 0);\n"

		for i in range(len(self.Splats)):
			out += "imageStore(mTDComputeOutputs[0], ivec3(gl_GlobalInvocationID.xy," + str(i) +  "), TDOutputSwizzle(" + "input" + str(i) +  "));\n"


		op.ShaderGGen.op('FinalGLslCompute').text = computeIn.replace("PLACEHOLDER_COMPUTE", out)

	def SetVertexShaderOutputs(self):
		# Add outputs to the vertex shader
		op.GGenLogger.Info('Set Vertex Shader Outputs')
		outVertexlist = ""
		for i in range(len(self.Splats)):
			outVertexlist += "float " + self.Splats[i].par.Paramname + ";\n"
		outVertex = op.ShaderGGen.op('OutVertex').text = '''
out Vertex
{
	vec4 color;
	mat3 tangentToWorld;
	vec3 worldSpacePos;
	vec3 pos;
	vec3 texCoord0;
	vec3 texCoord0_TexX;
	vec3 texCoord0_TexY;
	vec3 texCoord0_TexZ;
	flat int cameraIndex;
		''' + outVertexlist + '''
		
} oVert;

		'''
	
	def SetPixelShaderInputs(self):
		# Add inputs to the pixel shader
		op.GGenLogger.Info('Set Pixel Shader Inputs')
		inFragmentlist = ""
		for i in range(len(self.Splats)):
			inFragmentlist += "float " + self.Splats[i].par.Paramname + ";\n"
		InVertex = op.ShaderGGen.op('InVertex').text = '''
in Vertex
{
	vec4 color;
	mat3 tangentToWorld;
	vec3 worldSpacePos;
	vec3 pos;
	vec3 texCoord0;
	vec3 texCoord0_TexX;
	vec3 texCoord0_TexY;
	vec3 texCoord0_TexZ;
	flat int cameraIndex;
		''' + inFragmentlist + '''
} iVert;

		'''

	def SetVertexAttributes(self):
		# Add OutAttributes in vertex shader
		op.GGenLogger.Info('Set Vertex Attributes')
		outAttributesList = ""
		if len(self.Splats) == 0:
			outAttributesList += "oVert.pos = TDAttrib_P();\n"
		else:
			for i in range(len(self.Splats)):
				outAttributesList += "oVert." + self.Splats[i].par.Paramname +  " = " + "TDAttrib_" + self.Splats[i].par.Paramname + "();\n"
	
		op.ShaderGGen.op('OutAttributes').text = outAttributesList
	
	def SetMaterialAttributes(self):
		# Add Attributes in Material
		op.GGenLogger.Info('Set Material Attributes')

		# delete previous attributes
		#print('Existing attributes: ', op.ShaderGGen.op('TerrainPopShaderGLSL').seq.attr.numBlocks) 
		for i in range(op.ShaderGGen.op('TerrainPopShaderGLSL').seq.attr.numBlocks):
			if i > 4:  
				#print('Destroying block: ', i)

				op.ShaderGGen.op('TerrainPopShaderGLSL').seq.attr.destroyBlock(op.ShaderGGen.op('TerrainPopShaderGLSL').seq.attr.numBlocks - 1)  # Always destroy the last block
				#print('Remaining attributes: ', op.ShaderGGen.op('TerrainPopShaderGLSL').seq.attr.numBlocks)

		#print('Attributes after deletion: ', op.ShaderGGen.op('TerrainPopShaderGLSL').seq.attr.numBlocks)


		for i in range(len(self.Splats)):
			op.ShaderGGen.op('TerrainPopShaderGLSL').par["attr" + str(i+5) + "name"] = self.Splats[i].par.Paramname   

	def SetMaterialSamplers(self):
		# Add Samplers in material
		op.GGenLogger.Info('Set Material Samplers') 
		# for i in range(len(self.Splats)):
		# 	op.ShaderGGen.op('TerrainPopShaderGLSL').par["sampler" + str(i*3+5) + "name"] = self.Splats[i].par.Paramname + "Color"
		# 	op.ShaderGGen.op('TerrainPopShaderGLSL').par["sampler" + str(i*3+6) + "name"] = self.Splats[i].par.Paramname + "Normal"
		# 	op.ShaderGGen.op('TerrainPopShaderGLSL').par["sampler" + str(i*3+7) + "name"] = self.Splats[i].par.Paramname + "Roughness" 
		op.ShaderGGen.op('TerrainPopShaderGLSL').par["sampler5name"] = 's3dDiffuseMap'
		op.ShaderGGen.op('TerrainPopShaderGLSL').par["sampler6name"] = 's3dNormalMap'
		op.ShaderGGen.op('TerrainPopShaderGLSL').par["sampler7name"] = 's3dRoughnessMap'
		op.ShaderGGen.op('TerrainPopShaderGLSL').par["sampler8name"] = 's3dHeightMap'

	def BindSamplersToParameters(self):
		# Linking samplers to parent parameters
		op.GGenLogger.Info('Bind Samplers to Parameters')
		# for i in range(len(self.Splats)):  
		# 	op.ShaderGGen.op('TerrainPopShaderGLSL').par["sampler" + str(i*3+5) + "top"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(i) + "diffusemap"
		# 	op.ShaderGGen.op('TerrainPopShaderGLSL').par["sampler" + str(i*3+6) + "top"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(i) + "normalmap"
		# 	op.ShaderGGen.op('TerrainPopShaderGLSL').par["sampler" + str(i*3+7) + "top"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(i) + "roughnessmap"
		op.ShaderGGen.op('TerrainPopShaderGLSL').par["sampler5top"] = op.ShaderGGen.op('GLSL3DTextureRefiller')
		op.ShaderGGen.op('TerrainPopShaderGLSL').par["sampler6top"] = op.ShaderGGen.op('GLSL3DTextureRefiller1')
		op.ShaderGGen.op('TerrainPopShaderGLSL').par["sampler7top"] = op.ShaderGGen.op('GLSL3DTextureRefiller2')

	def SetGLSLSamplers(self):
		# add Samplers to GLSL
		op.GGenLogger.Info('Set GLSL Samplers')
		GLSLsamplers = ""
		for i in range(len(self.Splats)):
			GLSLsamplers += "uniform sampler2D " + self.Splats[i].par.Paramname + "Color;\n"
			GLSLsamplers += "uniform sampler2D " + self.Splats[i].par.Paramname + "Normal;\n"
			GLSLsamplers += "uniform sampler2D " + self.Splats[i].par.Paramname + "Roughness;\n"
		op.ShaderGGen.op('Samplers').text = GLSLsamplers

	def SetMaterialVectors(self):
		# add Vectors to Material
		op.GGenLogger.Info('Set Material Vectors') 

		# delete previous vectors
		for i in range(op('Shader/TerrainPopShaderGLSL').seq.vec.numBlocks):
			if i > 12:  
				op('Shader/TerrainPopShaderGLSL').seq.vec.destroyBlock(op('Shader/TerrainPopShaderGLSL').seq.vec.numBlocks - 1)  # Always destroy the last block
		
		# handle empty splat case
		if len(self.Splats) == 0:
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(13) + "name"] = "Base" + "UvTypeTileRotation"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(13) + "valuex"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(0) + "uv"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(13) + "valuey"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(0) + "tiling"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(13) + "valuez"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(0) + "rotation"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(13) + "valuew"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(0) + "noise"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(14) + "name"] = "Base" + "SplatDiffNorm"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(14) + "valuex"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(0) + "splatlevel"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(14) + "valuey"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(0) + "diffuselevel"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(14) + "valuez"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(0) + "normallevel"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(14) + "valuew"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(0) + "heightsmooth"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(15) + "name"] = "Base" + "DiffRoughNormHeight"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(15) + "valuex"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(0) + "diffuse"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(15) + "valuey"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(0) + "roughness"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(15) + "valuez"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(0) + "normal"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(15) + "valuew"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(0) + "parralax"

		# handle multiple splat case
		for i in range(len(self.Splats)):
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(i*3+13) + "name"] = self.Splats[i].par.Paramname + "UvTypeTileRotation"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(i*3+13) + "valuex"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(i) + "uv"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(i*3+13) + "valuey"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(i) + "tiling"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(i*3+13) + "valuez"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(i) + "rotation"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(i*3+13) + "valuew"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(i) + "noise"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(i*3+14) + "name"] = self.Splats[i].par.Paramname + "SplatDiffNorm"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(i*3+14) + "valuex"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(i) + "splatlevel"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(i*3+14) + "valuey"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(i) + "diffuselevel"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(i*3+14) + "valuez"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(i) + "normallevel"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(i*3+14) + "valuew"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(i) + "heightsmooth"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(i*3+15) + "name"] = self.Splats[i].par.Paramname + "DiffRoughNormHeight"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(i*3+15) + "valuex"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(i) + "diffuse"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(i*3+15) + "valuey"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(i) + "roughness"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(i*3+15) + "valuez"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(i) + "normal"
			op('Shader/TerrainPopShaderGLSL').par["vec" + str(i*3+15) + "valuew"].bindExpr = "op.ShaderGGen.par.Splatmaps" + str(i) + "parralax"

	def SetGLSLUniforms(self):
		# Set GLSL Uniforms
		op.GGenLogger.Info('Set GLSL Uniforms')
		uniforms = ""


		# handle empty splat case
		if len(self.Splats) == 0:
			uniforms += "uniform vec4 BaseUvTypeTileRotation;\n"
			uniforms += "uniform vec4 BaseSplatDiffNorm;\n"
			uniforms += "uniform vec4 BaseDiffRoughNormHeight;\n"

		# handle multiple splat case
		for i in range(len(self.Splats)):
			uniforms += "uniform vec4 " + self.Splats[i].par.Paramname + "UvTypeTileRotation;\n"
			uniforms += "uniform vec4 " + self.Splats[i].par.Paramname + "SplatDiffNorm;\n"
			uniforms += "uniform vec4 " + self.Splats[i].par.Paramname + "DiffRoughNormHeight;\n"
		
		
		
		op.ShaderGGen.op('Uniforms').text = uniforms

	def SetDefines(self):
		

		# Add splats to GLSL
		splats = ""
		# add splat maps
		op.GGenLogger.Info('Set Splats')
		splats += "\n// add splat maps\n"


		# handle empty splat case
		if len(self.Splats) == 0:
			splats += "float Base = clamp(1.0 * BaseSplatDiffNorm.x, 0,1);\n"

		# handle multiple splat case
		for i in range(len(self.Splats)):
			splats += "float " + self.Splats[i].par.Paramname + " = clamp(iVert." + self.Splats[i].par.Paramname + " * " +   self.Splats[i].par.Paramname + "SplatDiffNorm.x, 0,1)" +  ";\n"
		
		# add uvs 
		op.GGenLogger.Info('Set UVs')
		splats += "vec2 uvTop = iVert.texCoord0.st;\n"
		splats += "vec2 uvX = iVert.texCoord0_TexX.st;\n"
		splats += "vec2 uvY = iVert.texCoord0_TexY.st;\n"
		splats += "vec2 uvZ = iVert.texCoord0_TexZ.st;\n"

		op.ShaderGGen.op('Splats').text = splats


		# add parralax 1
		parralax1 = ""

		# handle empty splat case
		if len(self.Splats) == 0:
			parralax1 += "vec4 PreHeightBase = vec4(texture(s3dHeightMap, vec3(ApplyNoiseUv(uvTop * BaseDiffRoughNormHeight.w, BaseUvTypeTileRotation.y, BaseUvTypeTileRotation.w) * BaseUvTypeTileRotation.y, 0.5)));\n"
			parralax1 += "\n// use height to blend the textures\n"
			parralax1 += "float PreBaseBlendFactor = clamp(PreHeightBase.r * BaseSplatDiffNorm.x, 0, 1);\n"
			parralax1 += "\n// Blend textures\n"
			parralax1 += "float Prebase = 0;\n"
			parralax1 += "Base = clamp(Base + mix( Prebase, Base * 2, clamp(PreBaseBlendFactor * BaseSplatDiffNorm.x * 10, 0, 1)), 0, 1);\n"
			parralax1 += "\n// compute heights\n"
			parralax1 += "heightMapColor = mix(heightMapColor, PreHeightBase, Base);\n"
		else:
			#handle multiple splat Case
			
			for i in range(len(self.Splats)):
				parralax1 += "vec4 " + "PreHeight" + self.Splats[i].par.Paramname + " = vec4(texture(s3dHeightMap" + ", vec3(ApplyNoiseUv(uvTop * " + self.Splats[i].par.Paramname + "DiffRoughNormHeight.w, " + self.Splats[i].par.Paramname + "UvTypeTileRotation.y, " + self.Splats[i].par.Paramname + "UvTypeTileRotation.w) * " + self.Splats[i].par.Paramname + "UvTypeTileRotation.y,"+ str(i / len(self.Splats)+ 1 /len(self.Splats) /2) + ")" + "));\n"
				
			parralax1 += "\n// use height to blend the textures\n"
			for i in range(len(self.Splats)):
				parralax1 += "float Pre" + self.Splats[i].par.Paramname + "blendFactor = clamp(PreHeight" + self.Splats[i].par.Paramname + ".r * " + self.Splats[i].par.Paramname + ", 0, 1);\n"

			parralax1 += "\n// Blend textures\n"
			parralax1 += "float Prebase = 0;\n"
			for i in range(len(self.Splats)):
				if i > 0:
					parralax1 += self.Splats[i].par.Paramname  +" = clamp(" + self.Splats[i].par.Paramname + " + mix( Prebase, " + self.Splats[i].par.Paramname + " * 2, clamp(Pre" + self.Splats[i].par.Paramname + "blendFactor * " + self.Splats[i].par.Paramname + "SplatDiffNorm.x * 10, 0, 1)), 0, 1);\n"
			
			parralax1 += "\n// compute heights\n"
			for i in range(len(self.Splats)):
				parralax1 += "heightMapColor = mix(heightMapColor, PreHeight" + self.Splats[i].par.Paramname + ", " + self.Splats[i].par.Paramname + ");\n"


		op.ShaderGGen.op('Parralax1').text = parralax1


		# add parralax 2
		parralax2 = ""
		# handle empty splat case
		if len(self.Splats) == 0:
			parralax2 += "vec4 PreHeightBase = vec4(texture(s3dHeightMap, vec3(ApplyNoiseUv(currentTexCoords * BaseDiffRoughNormHeight.w, BaseUvTypeTileRotation.y, BaseUvTypeTileRotation.w) * BaseUvTypeTileRotation.y, 0.5)));\n"
			parralax2 += "\n// use height to blend the textures\n"
			parralax2 += "float PreBaseBlendFactor = clamp(PreHeightBase.r * BaseSplatDiffNorm.x, 0, 1);\n"
			parralax2 += "\n// Blend textures\n"
			parralax2 += "float Prebase = 0;\n"
			parralax2 += "Base = clamp(Base + mix( Prebase, Base * 2, clamp(PreBaseBlendFactor * BaseSplatDiffNorm.x * 10, 0, 1)), 0, 1);\n"
			parralax2 += "\n// compute heights\n"
			parralax2 += "heightMapColor = mix(heightMapColor, PreHeightBase, Base);\n"
		else:
			# handle multiple splat case
			for i in range(len(self.Splats)):
				parralax2 += "vec4 " + "PreHeight" + self.Splats[i].par.Paramname + " = vec4(texture(s3dHeightMap" + ", vec3(ApplyNoiseUv(currentTexCoords * " + self.Splats[i].par.Paramname + "DiffRoughNormHeight.w, " + self.Splats[i].par.Paramname + "UvTypeTileRotation.y, " + self.Splats[i].par.Paramname + "UvTypeTileRotation.w) * " + self.Splats[i].par.Paramname + "UvTypeTileRotation.y,"+ str(i / len(self.Splats)+ 1 /len(self.Splats) /2) + ")" + "));\n"
				
			parralax2 += "\n// use height to blend the textures\n"
			for i in range(len(self.Splats)):
				parralax2 += "float Pre" + self.Splats[i].par.Paramname + "blendFactor = clamp(PreHeight" + self.Splats[i].par.Paramname + ".r * " + self.Splats[i].par.Paramname + ", 0, 1);\n"

			parralax2 += "\n// Blend textures\n"
			parralax2 += "float Prebase = 0;\n"
			for i in range(len(self.Splats)):
				if i > 0:
					parralax2 += self.Splats[i].par.Paramname  +" = clamp(" + self.Splats[i].par.Paramname + " + mix( Prebase, " + self.Splats[i].par.Paramname + " * 2, clamp(Pre" + self.Splats[i].par.Paramname + "blendFactor * " + self.Splats[i].par.Paramname + "SplatDiffNorm.x * 10, 0, 1)), 0, 1);\n"
			
			parralax2 += "\n// compute heights\n"
			for i in range(len(self.Splats)):
				parralax2 += "heightMapColor = mix(heightMapColor, PreHeight" + self.Splats[i].par.Paramname + ", " + self.Splats[i].par.Paramname + ");\n"
				
		op.ShaderGGen.op('Parralax2').text = parralax2

		# add parralax 3
		parralax3 = ""
		# handle empty splat case
		if len(self.Splats) == 0:
			parralax3 += "PreHeightBase = vec4(texture(s3dHeightMap, vec3(ApplyNoiseUv(prevTexCoords * BaseDiffRoughNormHeight.w, BaseUvTypeTileRotation.y, BaseUvTypeTileRotation.w) * BaseUvTypeTileRotation.y, 0.5)));\n"
			parralax3 += "\n// use height to blend the textures\n"
			parralax3 += "PreBaseBlendFactor = clamp(PreHeightBase.r * BaseSplatDiffNorm.x, 0, 1);\n"
			parralax3 += "\n// Blend textures\n"
			parralax3 += "Prebase = 0;\n"
			parralax3 += "Prebase = clamp(Base + mix( Prebase, Base * 2, clamp(PreBaseBlendFactor * BaseSplatDiffNorm.x * 10, 0, 1)), 0, 1);\n"
			parralax3 += "\n// Blend heights\n"
			parralax3 += "heightMapColor = mix(heightMapColor, PreHeightBase, Base);\n"
		else:
			# handle multiple splat case
			for i in range(len(self.Splats)):
				parralax3 += "" + "PreHeight" + self.Splats[i].par.Paramname + " = vec4(texture(s3dHeightMap" + ", vec3(ApplyNoiseUv(prevTexCoords * " + self.Splats[i].par.Paramname + "DiffRoughNormHeight.w, " + self.Splats[i].par.Paramname + "UvTypeTileRotation.y, " + self.Splats[i].par.Paramname + "UvTypeTileRotation.w) * " + self.Splats[i].par.Paramname + "UvTypeTileRotation.y,"+ str(i / len(self.Splats)+ 1 /len(self.Splats) /2) + ")" + "));\n"
				
			parralax3 += "\n// use height to blend the textures\n"
			for i in range(len(self.Splats)):
				parralax3 += "Pre" + self.Splats[i].par.Paramname + "blendFactor = clamp(PreHeight" + self.Splats[i].par.Paramname + ".r * " + self.Splats[i].par.Paramname + ", 0, 1);\n"

			parralax3 += "\n// Blend textures\n"
			parralax3 += "Prebase = 0;\n"
			for i in range(len(self.Splats)):
				if i > 0:
					parralax3 += self.Splats[i].par.Paramname  +" = clamp(" + self.Splats[i].par.Paramname + " + mix( Prebase, " + self.Splats[i].par.Paramname + " * 2, clamp(Pre" + self.Splats[i].par.Paramname + "blendFactor * " + self.Splats[i].par.Paramname + "SplatDiffNorm.x * 10, 0, 1)), 0, 1);\n"
			
			parralax3 += "\n// Blend heights\n"
			for i in range(len(self.Splats)):
				parralax3 += "heightMapColor = mix(heightMapColor, PreHeight" + self.Splats[i].par.Paramname + ", " + self.Splats[i].par.Paramname + ");\n"
				
		op.ShaderGGen.op('Parralax3').text = parralax3

		# Add defines to GLSL
		op.GGenLogger.Info('Set Defines')
		defines = ""

		 
		# add splat Textures 
		op.GGenLogger.Info('Set Textures')

		if len(self.Splats) == 0:
			# handle single splat case
			# Check the splat map Uv type and add defines accordingly
			defines += "vec4 ColorBase = vec4(texture(s3dDiffuseMap, vec3(ApplyNoiseUv(uvTop, BaseUvTypeTileRotation.y, BaseUvTypeTileRotation.w) * BaseUvTypeTileRotation.y, 0.5)));\n"
			defines += "vec4 NormalBase = vec4(texture(s3dNormalMap, vec3(ApplyNoiseUv(uvTop, BaseUvTypeTileRotation.y, BaseUvTypeTileRotation.w) * BaseUvTypeTileRotation.y, 0.5)));\n"
			defines += "vec4 RoughnessBase = vec4(texture(s3dRoughnessMap, vec3(ApplyNoiseUv(uvTop, BaseUvTypeTileRotation.y, BaseUvTypeTileRotation.w) * BaseUvTypeTileRotation.y, 0.5)));\n"
			defines += "vec4 HeightBase = vec4(texture(s3dHeightMap, vec3(ApplyNoiseUv(uvTop, BaseUvTypeTileRotation.y, BaseUvTypeTileRotation.w) * BaseUvTypeTileRotation.y, 0.5)));\n"
			defines += "if(BaseUvTypeTileRotation.z == 1) NormalBase = vec4(-NormalBase.xy + 1,1,1);\n"
		else:
			# Handle multi-splat case
			for i in range(len(self.Splats)):
				# Check the splat map Uv type and add defines accordingly
				
				if len(self.Splats) == 1:
					defines += "vec4 " + "Color" + self.Splats[i].par.Paramname + " = vec4(texture(s3dDiffuseMap" + ", vec3(ApplyNoiseUv(uvTop, " + self.Splats[i].par.Paramname + "UvTypeTileRotation.y, " + self.Splats[i].par.Paramname + "UvTypeTileRotation.w) * " + self.Splats[i].par.Paramname + "UvTypeTileRotation.y,"+ str(i / len(self.Splats)+0.5) + ")" + "));\n"
					defines += "vec4 " + "Normal" + self.Splats[i].par.Paramname + " = vec4(texture(s3dNormalMap" + ", vec3(ApplyNoiseUv(uvTop, " + self.Splats[i].par.Paramname + "UvTypeTileRotation.y, " + self.Splats[i].par.Paramname + "UvTypeTileRotation.w) * " + self.Splats[i].par.Paramname + "UvTypeTileRotation.y,"+ str(i / len(self.Splats)+0.5) + ")" + "));\n"
					defines += "vec4 " + "Roughness" + self.Splats[i].par.Paramname + " = vec4(texture(s3dRoughnessMap" + ", vec3(ApplyNoiseUv(uvTop, " + self.Splats[i].par.Paramname + "UvTypeTileRotation.y, " + self.Splats[i].par.Paramname + "UvTypeTileRotation.w) * " + self.Splats[i].par.Paramname + "UvTypeTileRotation.y,"+ str(i / len(self.Splats)+0.5) + ")" + "));\n"
					defines += "vec4 " + "Height" + self.Splats[i].par.Paramname + " = vec4(texture(s3dHeightMap" + ", vec3(ApplyNoiseUv(uvTop, " + self.Splats[i].par.Paramname + "UvTypeTileRotation.y, " + self.Splats[i].par.Paramname + "UvTypeTileRotation.w) * " + self.Splats[i].par.Paramname + "UvTypeTileRotation.y,"+ str(i / len(self.Splats)+0.5) + ")" + "));\n"
				else:
					defines += "vec4 " + "Color" + self.Splats[i].par.Paramname + " = vec4(texture(s3dDiffuseMap" + ", vec3(ApplyNoiseUv(uvTop, " + self.Splats[i].par.Paramname + "UvTypeTileRotation.y, " + self.Splats[i].par.Paramname + "UvTypeTileRotation.w) * " + self.Splats[i].par.Paramname + "UvTypeTileRotation.y,"+ str(i / len(self.Splats)+ 1 / len(self.Splats)/2) + ")" + "));\n"
					defines += "vec4 " + "Normal" + self.Splats[i].par.Paramname + " = vec4(texture(s3dNormalMap" + ", vec3(ApplyNoiseUv(uvTop, " + self.Splats[i].par.Paramname + "UvTypeTileRotation.y, " + self.Splats[i].par.Paramname + "UvTypeTileRotation.w) * " + self.Splats[i].par.Paramname + "UvTypeTileRotation.y,"+ str(i / len(self.Splats)+ 1 /len(self.Splats)/2) + ")" + "));\n"
					defines += "vec4 " + "Roughness" + self.Splats[i].par.Paramname + " = vec4(texture(s3dRoughnessMap" + ", vec3(ApplyNoiseUv(uvTop, " + self.Splats[i].par.Paramname + "UvTypeTileRotation.y, " + self.Splats[i].par.Paramname + "UvTypeTileRotation.w) * " + self.Splats[i].par.Paramname + "UvTypeTileRotation.y,"+ str(i / len(self.Splats)+ 1 /len(self.Splats) /2) + ")" + "));\n"
					defines += "vec4 " + "Height" + self.Splats[i].par.Paramname + " = vec4(texture(s3dHeightMap" + ", vec3(ApplyNoiseUv(uvTop, " + self.Splats[i].par.Paramname + "UvTypeTileRotation.y, " + self.Splats[i].par.Paramname + "UvTypeTileRotation.w) * " + self.Splats[i].par.Paramname + "UvTypeTileRotation.y,"+ str(i / len(self.Splats)+ 1 /len(self.Splats) /2) + ")" + "));\n"
				defines += "if(" + self.Splats[i].par.Paramname + "SplatDiffNorm.z == 1) Normal" + self.Splats[i].par.Paramname + " = vec4(-Normal" + self.Splats[i].par.Paramname + ".xy + 1,1,1);\n"	
	
		if len(self.Splats) == 0:
			# Handle single splat case
			defines += "\n// threshold with smoothstep\n"
			defines += "HeightBase.r = smoothstep(BaseSplatDiffNorm.y - BaseSplatDiffNorm.w/2, BaseSplatDiffNorm.y + BaseSplatDiffNorm.w/2, HeightBase.r);\n"
			defines += "\n// use height to blend the textures\n"
			defines += "float BaseBlendFactor = clamp(HeightBase.r * Base,0,1);\n"
			defines += "\n// Blend textures\n"
			defines += "float base = 0;\n"
			defines += "Base = clamp(Base + mix( base, Base * 2, clamp(BaseBlendFactor * BaseSplatDiffNorm.x * 10, 0, 1)), 0, 1);\n"


		else:	
			#handle multi-splat case
			# threshold at 0.5 with smoothstep
			defines += "\n// threshold with smoothstep\n"
			
			for i in range(len(self.Splats)):
				defines += "Height" + self.Splats[i].par.Paramname + ".r = smoothstep(" + self.Splats[i].par.Paramname + "SplatDiffNorm.y -" + self.Splats[i].par.Paramname + "SplatDiffNorm.w/2, " + self.Splats[i].par.Paramname + "SplatDiffNorm.y + " + self.Splats[i].par.Paramname + "SplatDiffNorm.w/2, Height" + self.Splats[i].par.Paramname + ".r);\n"
			
			# use height to blend the textures
			defines += "\n// use height to blend the textures\n"
			for i in range(len(self.Splats)):
				defines += "float " + self.Splats[i].par.Paramname + "blendFactor = clamp(Height" + self.Splats[i].par.Paramname + ".r * " + self.Splats[i].par.Paramname + ", 0, 1);\n"


			# Blend textures
			defines += "\n// Blend textures\n"
			defines += "float base = 0;\n"
			for i in range(len(self.Splats)):
				if i > 0:
					defines += self.Splats[i].par.Paramname  +" = clamp(" + self.Splats[i].par.Paramname + " + mix( base, " + self.Splats[i].par.Paramname + " * 2, clamp(" + self.Splats[i].par.Paramname + "blendFactor * " + self.Splats[i].par.Paramname + "SplatDiffNorm.x * 10, 0, 1)), 0, 1);\n"


		op.ShaderGGen.op('Defines').text = defines

	def AddNormalMapComputing(self):
		# Add multitexture normal computing to GLSL 
		op.GGenLogger.Info('Add Normal Map Computing')
		normals = ""
		# handle empty splat case
		if len(self.Splats) == 0:
			normals += "normalMap = NormalBase;\n"
			normals += "normalMap = vec4(PNDMix(normalMap.xyz, NormalBase.xyz, Base), 1, 1);\n"
		else:
			# handle multi-splat case
			normals += "normalMap = Normal" + self.Splats[0].par.Paramname + ";\n" 

			for i in range(len(self.Splats)):
				# Add multitexture normal
				
				#normals += "normalMap = vec4(PartialNormalDerivatives(" + "Normal" + self.Splats[i].par.Paramname +".xyz, mix(Nbase.xyz, " + "Normal" + self.Splats[i].par.Paramname + ".xyz" + ", " + self.Splats[i].par.Paramname +  ")" + "),1,1) ;\n"
				normals += "normalMap = vec4(PNDMix(normalMap.xyz, Normal" + self.Splats[i].par.Paramname + ".xyz, " + self.Splats[i].par.Paramname + "),1,1);\n"
		
		
		op.ShaderGGen.op('Normals').text = normals

	def SetColorComputing(self):
		
		# Add multitexture color computing to GLSL 
		op.GGenLogger.Info('Add Color Computing')
		colors = ""

		# handle empty splat case
		if len(self.Splats) == 0:
			colors += "baseColorMap = ColorBase;\n" 
			colors += "baseColorMap = mix(baseColorMap, ColorBase, Base);\n" 
			colors += '''
	vec4 groundCol = vec4(0.3,0.2,0.1,1);
	vec4 grassCol = vec4(0,0.3,0,1);
	vec4 stoneCol = vec4(0.3,0.3,0.3,1);
	vec4 snowCol = vec4(0.5,0.5,0.5,1);


	// simple layered shader using wordspaceposistion 

	float ground = smoothstep(-3,-1, iVert.pos.y);
	float grass = smoothstep(-1,0, iVert.pos.y);
	float stone = smoothstep(0, 2, iVert.pos.y);
	float snow = smoothstep(2, 10, iVert.pos.y);

	vec4 layeredColor = mix(groundCol, grassCol, grass);

	layeredColor = mix(layeredColor, stoneCol, stone);
	layeredColor = mix(layeredColor, snowCol, snow);
	baseColorMap = layeredColor;'''
		else:
			# handle multi-splat case
			colors += "baseColorMap = Color" + self.Splats[0].par.Paramname + ";\n"
			for i in range(len(self.Splats)):
				# Add multitexture color
				colors += "baseColorMap = mix(" + "baseColorMap" + ", " + "Color" + self.Splats[i].par.Paramname + ", " + self.Splats[i].par.Paramname + ");\n"
		
		
		op.ShaderGGen.op('Colors').text = colors

		pass
	 
	def SetRoughnessComputing(self): 
		# Add multitexture roughness computing to GLSL
		op.GGenLogger.Info('Add Roughness Computing')

		roughs = ""

		# handle empty splat case
		if len(self.Splats) == 0:
			roughs += "roughnessMapColor = RoughnessBase;\n"
			roughs += "roughnessMapColor = mix(roughnessMapColor, RoughnessBase, Base);\n"
		else:
			roughs += "roughnessMapColor = Roughness" + self.Splats[0].par.Paramname + ";\n"

			for i in range(len(self.Splats)):
				# Add multitexture roughness
				roughs += "roughnessMapColor = mix(roughnessMapColor, " + "Roughness" + self.Splats[i].par.Paramname + ", " + self.Splats[i].par.Paramname + ");\n"
		
		op.ShaderGGen.op('Roughs').text = roughs
		pass
	
	def SetShaderParams(self):
		op.GGenLogger.Info('Set Shader Params from Config')
		configPath = op.GGen.par.Ggenfolder + "/config.json"
		print("Loading config from: " + configPath)
		
		# if exists
		config = {}
		if os.path.exists(configPath):
			with open(configPath, 'r') as f:
				config = json.load(f)
		else:
			return
		
		shader = op.ShaderGGen 
		params = config['Shader']

		#apply params to shader

		try:
			for key in params:
				
				name = str(key['name'])
				value = key['value']
				#print("Setting shader param: " + name + " to value: " + str(value))
				op.ShaderGGen.par[name] = value
		except:
			pass
